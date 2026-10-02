---
name: make-video
description: Edit supplied photos or video footage and music into a finished montage, travel film, slideshow, or reference-inspired sequence. Use for shot selection, musical pacing, motion design, stabilization, cinematic grading, revisions, and verified video exports through Resolve or command-line workflows.
---

# Make Video

Turn the user's media, soundtrack, and target into a finished, reviewable edit. Make editorial decisions from actual pictures and music. Preserve editable sources and a reproducible timeline alongside the delivery.

## Establish the edit

Recover existing project notes and completed steps before starting a revision. Reconcile uncertain renders, uploads, and shares from their recorded IDs and current state before repeating a write.

Use supplied preferences for reference, aspect ratio, approximate length, music start, must-use material, delivery color space, and destination. Ask only for missing decisions that materially affect the result; otherwise state reasonable assumptions and proceed. A prior project's 24 fps, three-second cuts, or day-to-night story are examples, not universal defaults. Clarify ambiguous “original quality” in terms of resolution, frame rate, bit depth, and SDR/HDR.

Inventory originals: dimensions, orientation, duration, frame rate/time base, audio, bit depth, color primaries/transfer/matrix/range, and still-image profiles. Keep sources unchanged. Use proxies for analysis and originals for finishing.

Inspect every asset before placing it. For video, examine beginning/middle/end and moving passages; for stills, examine the full image and proposed crop. Record subject, action, camera motion, usable range, lighting/time-of-day evidence, and flaws. Choose order from these observations, not filenames alone. Mark uncertain inferences.

## Design the sequence

Read [editing.md](references/editing.md) for reference analysis, music phrasing, photo motion, and shot ordering. Build a frame-based manifest containing source IDs/paths, selected ranges or image holds, timeline start and duration, transforms, grade intent, music offset, and transitions. Use integer frame boundaries and rational frame rate; define ranges as half-open `[start, end)` and translate at editor boundaries.

Establish opening, buildup, main sequence, and ending before polishing effects. Inspect the actual reference interval and soundtrack when available. Match relevant pacing and visual language; a reference edit may rearrange the song. Render a short representative proof with a cut, music, grade, and any graphics before processing everything.

## Choose the production path

Respect the user's chosen editor when workable. Verify installed capabilities with a small successful operation before relying on automation.

- **Photos plus music, straightforward SDR montage:** read [stills-renderer.md](references/stills-renderer.md) and use the bundled renderer when its supported framing and motion fit. It does not replace inspecting and ordering images.
- **Footage, complex grading, or editable Resolve delivery:** read [resolve.md](references/resolve.md). Use scripts/imports for exact timing and supported GUI controls for visual finishing.
- **OSS workflow:** FFmpeg/ffprobe handle inspection, preparation, and deterministic renders. MLT with Shotcut or Kdenlive can provide an editable timeline; start from a project authored by the installed editor so its native metadata survives. Blender can handle custom compositing. Verify current official documentation for unfamiliar APIs.

For footage stabilization, mixed source color, HDR, or cinematic regrading, read [color-and-stabilization.md](references/color-and-stabilization.md) before building intermediates. Match individual shots, then apply the shared look. Keep highlights, faces, and motivated lighting believable; saturation and sharpening are not shortcuts to a film look.

Use motion graphics where they serve the target: intentional entrance, readable hold, resolved exit. Keep movement subordinate to subject and music. Save the editable project and external graphics/LUTs with relative or documented media links.

## Finish and verify

Read [delivery-and-qa.md](references/delivery-and-qa.md) before final encoding. Inspect actual rendered cuts, frames, and audio. Verify dimensions, frame count, frame rate, codec/pixel format, color metadata, and complete decode. Distinguish measured checks from listening, motion playback, or calibrated HDR review that was not performed.

For remote ingest or requested upload, read [remote-media.md](references/remote-media.md). Upload and public sharing require user authorization for that destination; making a local video does not imply publication. Verify a requested public link as an unauthenticated viewer.

Completion means the requested final file exists and passes relevant checks, editable work is saved, and requested upload is reconciled and verified. Report the file/link, delivery specs, and material limitations. Close the editor normally after saving when asked; preserve the project for revisions.
