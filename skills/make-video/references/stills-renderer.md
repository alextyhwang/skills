# Small, deterministic photo renderer

Use `scripts/render_stills.py` for an SDR photo montage with hard cuts and optional gentle, centered zooms. It does not choose the photographs, sequence, grade, crop focal points, music phrasing, titles, or transitions: make those editorial decisions first. Use an NLE for footage, HDR, animated typography, audio mixing, transitions, or customized motion paths.

Requires Python 3.10+, Pillow (`python -m pip install Pillow`), and FFmpeg/ffprobe with the libx264 encoder. Pass executable paths if they are not on PATH. Only ordinary 8-bit JPEG, PNG, and WebP stills are supported; HDR, gain maps, high-bit-depth images, animation, HEIC, and AVIF need an explicit color-managed preparation step. Metadata checks cannot prove that an untagged image is SDR. Confirm source interpretation yourself. Untagged RGB is assumed sRGB; valid ICC profiles are converted to sRGB; EXIF orientation is applied. Transparency is composited on black.

```json
{
  "color_space": "sdr-srgb",
  "width": 1920,
  "height": 1080,
  "fps": "24",
  "music": {
    "path": "music.wav",
    "offset_seconds": 0,
    "gain_db": -3,
    "fade_out_seconds": 1
  },
  "shots": [
    {"image": "photos/morning.jpg", "frames": 96, "fit": "cover", "zoom": [1, 1.035]},
    {"image": "photos/evening.png", "frames": 96, "fit": "contain"}
  ]
}
```

Paths resolve relative to the manifest, not the working directory. Absolute paths also work. Width and height must be even integers, 16–7680; frame rate is a rational string, 1–120 (for example `24000/1001`). Each shot requires a positive integer frame count. Cuts occur at cumulative frame counts: the example cuts at frame 96 and ends at frame 192. Do not derive each boundary by rounding independent decimal durations.

`fit` defaults to `contain`, which preserves the entire image with black margins. `cover` fills the frame using a centered crop: inspect faces and subjects before choosing it. `zoom` defaults to `[1, 1]`; its two values must be within 1–1.15. It zooms the fitted canvas, including any margins, using twice-resolution oversampling. It does not infer focal points or invent parallax. Use static images where motion would distract.

Music offset is nonnegative seconds; gain is -60 to +12 dB, default 0; final linear amplitude fade is 0 through the edit duration, default 1 second. The source must cover the complete edit after the offset. For edits shorter than one second, set a shorter explicit fade. The renderer neither loops nor pads missing music. Choose a musical ending; a fade cannot fix a poor endpoint. Positive gain can clip: assess peaks/loudness and audition the export separately.

```sh
python scripts/render_stills.py edit.json output-v1.mp4 --validate-only
python scripts/render_stills.py edit.json output-v1.mp4
```

An explicit `--ffmpeg /path/to/ffmpeg --ffprobe /path/to/ffprobe` works with both commands. Validation inspects every image and checks the music duration. Rendering writes temporary intermediates beside the output, converts sRGB transfer to BT.709 before matrix conversion, encodes H.264 CRF 17 with AAC stereo at 48 kHz, verifies frame count/frame rate/dimensions/color tags, then fully decodes the result before committing the final file. It refuses to overwrite an existing output; choose a new version name. The final commit uses a same-volume hard link, so use a filesystem supporting hard links. Temporary files are cleaned on ordinary failure; interruption may leave a `.make-video-*` folder, which can be inspected and removed after confirming no render is active.

Output is **8-bit SDR BT.709**, not an original-quality HDR master. Source files remain unchanged. Structural validation does not replace visual review, listening, or inspecting crop, compression, brightness, motion and cut placement. AAC packet padding can make the container duration slightly longer than the exact video frame duration.

Run the synthetic integration checks without private media:

```sh
python scripts/test_render_stills.py --ffmpeg /path/to/ffmpeg --ffprobe /path/to/ffprobe
```
