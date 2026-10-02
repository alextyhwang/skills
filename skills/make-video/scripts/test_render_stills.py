#!/usr/bin/env python3
"""Synthetic render integration checks; creates no persistent media."""
import argparse
import copy
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import wave
import math

from PIL import Image, ImageCms

import render_stills as renderer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', default='ffmpeg')
    parser.add_argument('--ffprobe', default='ffprobe')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='make-video-test-') as directory:
        root = Path(directory)
        for name, color in [('red', (230, 10, 10)), ('green', (10, 230, 10)), ('blue', (10, 10, 230))]:
            Image.new('RGB', (420, 280), color).save(root / f'{name}.png')
        exif = Image.Exif()
        exif[274] = 6
        Image.new('RGB', (40, 20), 'red').save(root / 'oriented.jpg', exif=exif)
        assert renderer.load_image(root / 'oriented.jpg').size == (20, 40)
        profile = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
        Image.new('RGB', (20, 20), (120, 40, 20)).save(root / 'profile.png', icc_profile=profile)
        assert renderer.load_image(root / 'profile.png').getpixel((0, 0)) == (120, 40, 20)
        Image.new('RGBA', (20, 20), (255, 0, 0, 0)).save(root / 'alpha.png')
        assert renderer.load_image(root / 'alpha.png').getpixel((0, 0)) == (0, 0, 0)
        with wave.open(str(root / 'music.wav'), 'wb') as wav:
            wav.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
            wav.writeframes(b''.join(struct.pack('<h', round(6000 * math.sin(i * 2 * math.pi * 440 / 48000))) for i in range(4 * 48000)))
        data = {'color_space': 'sdr-srgb', 'width': 320, 'height': 180, 'fps': '30000/1001',
                'music': {'path': 'music.wav', 'offset_seconds': 0.2, 'gain_db': -3, 'fade_out_seconds': 0.3},
                'shots': [{'image': f'{color}.png', 'frames': frames, 'fit': 'cover', 'zoom': [1, 1.035]}
                          for color, frames in [('red', 17), ('green', 23), ('blue', 31)]]}
        manifest = root / 'edit.json'
        manifest.write_text(json.dumps(data))
        parsed = renderer.validate(manifest, args.ffprobe)
        output = root / 'result.mp4'
        report = renderer.render(parsed, output, args.ffmpeg, args.ffprobe)
        assert report['frames'] == 71
        # Verify actual decoded colors on both sides of every cut, not just metadata.
        frames = subprocess.run([args.ffmpeg, '-v', 'error', '-i', str(output), '-vf', 'scale=1:1',
                                 '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
        assert len(frames) == 71 * 3
        for index, channel in [(0, 0), (16, 0), (17, 1), (39, 1), (40, 2), (70, 2)]:
            rgb = frames[index*3:index*3+3]
            assert rgb[channel] > 140 and all(rgb[channel] > rgb[j] * 3 for j in range(3) if j != channel), (index, rgb)
        decoded = subprocess.run([args.ffmpeg, '-v', 'error', '-i', str(output), '-map', '0:a:0',
                                  '-f', 'f32le', '-ac', '1', '-'], capture_output=True, check=True).stdout
        audio = struct.unpack('<' + 'f' * (len(decoded)//4), decoded)
        assert max(abs(v) for v in audio) < 0.5
        end = round(71 * 48000 * 1001 / 30000)
        assert max(abs(v) for v in audio[end-240:end]) < 0.004
        try:
            renderer.render(parsed, output, args.ffmpeg, args.ffprobe)
            raise AssertionError('Existing output was overwritten')
        except ValueError as exc:
            assert 'overwrite' in str(exc)
        invalid = []
        for field, value in [('width', 321), ('fps', '0'), ('color_space', 'rec2100-hlg')]:
            bad = copy.deepcopy(data)
            bad[field] = value
            invalid.append(bad)
        for field, value in [('frames', 0), ('frames', True), ('image', 'absent.png'), ('zoom', [1, 2])]:
            bad = copy.deepcopy(data)
            bad['shots'][0][field] = value
            invalid.append(bad)
        bad = copy.deepcopy(data)
        bad['music']['offset_seconds'] = 10
        invalid.append(bad)
        Image.new('I;16', (16, 16), 1000).save(root / 'high-depth.png')
        bad = copy.deepcopy(data)
        bad['shots'][0]['image'] = 'high-depth.png'
        invalid.append(bad)
        for bad in invalid:
            manifest.write_text(json.dumps(bad))
            try:
                renderer.validate(manifest, args.ffprobe)
                raise AssertionError(f'Invalid manifest accepted: {bad}')
            except ValueError:
                pass
        print(json.dumps({'render': report, 'cut_boundaries': 'passed', 'audio_fade_and_peak': 'passed',
                          'overwrite_protection': 'passed', 'invalid_inputs_rejected': len(invalid)}))


if __name__ == '__main__':
    main()
