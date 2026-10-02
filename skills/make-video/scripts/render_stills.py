#!/usr/bin/env python3
"""Render an explicit frame-based SDR photo edit. See ../references/stills-renderer.md."""
import argparse
import io
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction

from PIL import Image, ImageCms, ImageOps


def run(args):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f"Command failed: {args[0]}\n{result.stderr[-6000:]}")
    return result.stdout


def probe(binary, path):
    return json.loads(run([binary, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path]))


def number(value, name, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'{name} must be a finite number between {low} and {high}')
    return value


def fields(value, allowed, name):
    if not isinstance(value, dict):
        raise ValueError(f'{name} must be an object')
    unknown = set(value) - set(allowed)
    if unknown:
        raise ValueError(f'Unknown {name} fields: {sorted(unknown)}')


def source(base, value):
    if not isinstance(value, str) or not value:
        raise ValueError('Source paths must be nonempty strings')
    path = (base / value).resolve()
    if not path.is_file():
        raise ValueError(f'Missing source: {path}')
    return path


def load_image(path):
    with Image.open(path) as original:
        if original.format not in ('JPEG', 'PNG', 'WEBP'):
            raise ValueError(f'Unsupported image format: {path.name}; prepare an SDR JPEG/PNG/WebP first')
        if original.format == 'PNG':
            with path.open('rb') as f:
                header = f.read(25)
            if len(header) < 25 or header[24] > 8:
                raise ValueError(f'High bit depth PNG is unsupported: {path.name}')
        keys = {str(k).lower() for k in original.info}
        if original.mode in ('I', 'F', 'I;16', 'I;16B') or getattr(original, 'n_frames', 1) != 1:
            raise ValueError(f'High bit depth or animated image is unsupported: {path.name}')
        if keys.intersection({'mp', 'mpf', 'cicp'}) or any('hdr' in k or 'gainmap' in k for k in keys):
            raise ValueError(f'HDR/multi-picture metadata requires manual color preparation: {path.name}')
        xmp = original.info.get('xmp', b'')
        if any(term in str(xmp).lower() for term in ('hdrgm', 'gainmap', 'hdrgainmap')):
            raise ValueError(f'Gain-map image requires manual SDR preparation: {path.name}')
        profile = original.info.get('icc_profile')
        im = ImageOps.exif_transpose(original)
        alpha = im.convert('RGBA').getchannel('A') if 'A' in im.getbands() or 'transparency' in im.info else None
        if profile:
            try:
                im = ImageCms.profileToProfile(im.convert('RGB') if im.mode not in ('RGB', 'CMYK', 'LAB', 'L') else im,
                    ImageCms.ImageCmsProfile(io.BytesIO(profile)), ImageCms.createProfile('sRGB'), outputMode='RGB')
            except Exception as exc:
                raise ValueError(f'Cannot convert ICC profile for {path.name}: {exc}') from exc
        else:
            if im.mode == 'CMYK':
                raise ValueError(f'CMYK image needs an ICC profile: {path.name}')
            im = im.convert('RGB')
        if alpha is not None:
            black = Image.new('RGB', im.size)
            black.paste(im, mask=alpha)
            im = black
        return im.copy()


def validate(manifest, ffprobe):
    data = json.loads(manifest.read_text(encoding='utf-8'))
    fields(data, ('color_space', 'width', 'height', 'fps', 'music', 'shots'), 'manifest')
    if data.get('color_space') != 'sdr-srgb':
        raise ValueError("Set color_space to 'sdr-srgb' only after confirming SDR input; HDR is unsupported")
    for key in ('width', 'height'):
        v = data.get(key)
        if type(v) is not int or v < 16 or v > 7680 or v % 2:
            raise ValueError(f'{key} must be an even integer from 16 through 7680')
    if not isinstance(data.get('fps'), str):
        raise ValueError('fps must be a rational string, e.g. "24" or "24000/1001"')
    fps = Fraction(data['fps'])
    if not 1 <= fps <= 120:
        raise ValueError('fps must be between 1 and 120')
    shots = data.get('shots')
    if not isinstance(shots, list) or not shots:
        raise ValueError('shots must be a nonempty list')
    for i, shot in enumerate(shots):
        fields(shot, ('image', 'frames', 'fit', 'zoom'), f'shot {i}')
        if type(shot.get('frames')) is not int or shot['frames'] < 1:
            raise ValueError(f'Shot {i}: frames must be a positive integer')
        if shot.get('fit', 'contain') not in ('contain', 'cover'):
            raise ValueError(f'Shot {i}: fit must be contain or cover')
        zoom = shot.get('zoom', [1, 1])
        if not isinstance(zoom, list) or len(zoom) != 2:
            raise ValueError(f'Shot {i}: zoom must contain two numbers')
        for z in zoom:
            number(z, 'zoom', 1, 1.15)
        shot['_path'] = source(manifest.parent, shot.get('image'))
        load_image(shot['_path'])
    music = data.get('music', {})
    fields(music, ('path', 'offset_seconds', 'gain_db', 'fade_out_seconds'), 'music')
    music['_path'] = source(manifest.parent, music.get('path'))
    total = sum(s['frames'] for s in shots)
    duration = float(total / fps)
    number(music.get('offset_seconds', 0), 'music offset', 0, 1e9)
    number(music.get('gain_db', 0), 'music gain_db', -60, 12)
    number(music.get('fade_out_seconds', 1), 'music fade', 0, duration)
    info = probe(ffprobe, music['_path'])
    audio = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
    if not audio:
        raise ValueError('Music source has no audio stream')
    available = float(audio.get('duration') or info['format'].get('duration', 0))
    if available + 0.001 < music.get('offset_seconds', 0) + duration:
        raise ValueError('Music is shorter than the requested edit and offset; choose a real ending or provide longer music')
    data['_fps'], data['_frames'], data['_duration'] = fps, total, duration
    return data


def gamma_to_709(im):
    # Convert sRGB encoded RGB into BT.709 encoded RGB before YCbCr matrix conversion.
    table = []
    for n in range(256):
        v = n / 255
        linear = v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
        encoded = 4.5 * linear if linear < 0.018 else 1.099 * linear ** 0.45 - 0.099
        table.append(round(max(0, min(1, encoded)) * 255))
    return im.point(table * 3)


def render(data, output, ffmpeg, ffprobe):
    if output.suffix.lower() != '.mp4':
        raise ValueError('Output must end in .mp4')
    if output.exists():
        raise ValueError(f'Refusing to overwrite {output}')
    output.parent.mkdir(parents=True, exist_ok=True)
    width, height = data['width'], data['height']
    fps = str(data['_fps'])
    color = ['-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv']
    with tempfile.TemporaryDirectory(prefix='.make-video-', dir=output.parent) as tmp:
        tmp = Path(tmp)
        pieces = []
        for i, shot in enumerate(data['shots']):
            im = load_image(shot['_path'])
            # Oversample zoom animation to limit integer-crop jitter.
            size = (width * 2, height * 2)
            if shot.get('fit', 'contain') == 'cover':
                canvas = ImageOps.fit(im, size, method=Image.Resampling.LANCZOS)
            else:
                scaled = ImageOps.contain(im, size, method=Image.Resampling.LANCZOS)
                canvas = Image.new('RGB', size)
                canvas.paste(scaled, ((size[0] - scaled.width) // 2, (size[1] - scaled.height) // 2))
            image = tmp / f'{i:05d}.png'
            gamma_to_709(canvas).save(image)
            a, b = shot.get('zoom', [1, 1])
            frames = shot['frames']
            zoom = f'{a}+({b}-{a})*on/{max(1, frames-1)}'
            vf = (f"zoompan=z='{zoom}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':"
                  f'd={frames}:s={width}x{height}:fps={fps},'
                  'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,'
                  'setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709')
            clip = tmp / f'{i:05d}.mp4'
            run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-i', image, '-vf', vf,
                 '-frames:v', frames, '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                 *color, '-video_track_timescale', data['_fps'].numerator, clip])
            pieces.append(clip)
        listing = tmp / 'concat.txt'
        listing.write_text(''.join(f"file '{p.name}'\n" for p in pieces), encoding='utf-8')
        music = data['music']
        duration = data['_duration']
        samples = round(data['_frames'] * 48000 / data['_fps'])
        af = f"aresample=48000,atrim=end_sample={samples},asetpts=PTS-STARTPTS,volume={music.get('gain_db', 0)}dB"
        fade = music.get('fade_out_seconds', 1)
        if fade:
            af += f',afade=t=out:st={duration-fade:.12f}:d={fade:.12f}'
        result = tmp / 'finished.mp4'
        run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', listing,
             '-ss', music.get('offset_seconds', 0), '-i', music['_path'], '-map', '0:v:0', '-map', '1:a:0',
             '-c:v', 'copy', '-af', af, '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-ac', '2',
             '-movflags', '+faststart', result])
        info = probe(ffprobe, result)
        video = next(s for s in info['streams'] if s['codec_type'] == 'video')
        audio = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
        if not audio or audio.get('sample_rate') != '48000' or audio.get('channels') != 2:
            raise ValueError('Export is missing the expected 48 kHz stereo audio')
        if (int(video.get('nb_frames', 0)) != data['_frames'] or video['width'] != width or video['height'] != height
            or Fraction(video['avg_frame_rate']) != data['_fps'] or video['pix_fmt'] != 'yuv420p'
            or any(video.get(k) != 'bt709' for k in ('color_primaries', 'color_transfer', 'color_space'))):
            raise ValueError(f'Export does not match requested frame/color specification: {video}')
        run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-xerror', '-i', result, '-f', 'null', '-'])
        # Same filesystem hard-link commit refuses an existing name, including a racing writer.
        os.link(result, output)
    return {'output': str(output), 'frames': data['_frames'], 'fps': fps, 'duration_seconds': duration,
            'color': '8-bit SDR BT.709', 'full_decode': 'passed'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--ffmpeg', default='ffmpeg', help='FFmpeg executable (must include libx264)')
    parser.add_argument('--ffprobe', default='ffprobe')
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    try:
        for binary in (args.ffmpeg, args.ffprobe):
            if not shutil.which(binary):
                raise ValueError(f'Executable unavailable: {binary}')
        data = validate(args.manifest.resolve(), args.ffprobe)
        if args.validate_only:
            print(json.dumps({'valid': True, 'frames': data['_frames'], 'duration_seconds': data['_duration']}))
        else:
            print(json.dumps(render(data, args.output.resolve(), args.ffmpeg, args.ffprobe)))
    except (ValueError, OSError, KeyError, TypeError, ZeroDivisionError) as exc:
        parser.exit(1, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
