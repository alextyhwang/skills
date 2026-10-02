# Skills

Reusable [Agent Skills](https://agentskills.io/specification) for practical creative work.

## make-video

Edit photos or footage and music into a finished montage, travel film, or reference-inspired sequence. Covers shot selection, musical pacing, photo motion, Resolve, stabilization, restrained grading, HDR verification, and resumable delivery.

Install with the [skills CLI](https://skills.sh/docs/cli):

```sh
npx skills add alextyhwang/skills --skill make-video --global
```

Or select agents explicitly:

```sh
npx skills add alextyhwang/skills --skill make-video --global --agent codex claude-code
```

Example:

> Use $make-video with these photos and this music. Make a 30-second landscape film with a quiet opening, gentle motion, and a resolved musical ending. Export an SDR MP4 and keep the editable timing manifest.

Supply media, music, and any reference/delivery preferences. Automatic discovery and explicit invocation are supported. Instructions are editor-independent; the bundled still-image renderer requires Python, Pillow, FFmpeg, and ffprobe and supports SDR output. HDR and complex footage use a separately verified finishing pipeline.

Entry point: [skills/make-video/SKILL.md](skills/make-video/SKILL.md).
