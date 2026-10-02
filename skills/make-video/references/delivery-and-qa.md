# Delivery and evidence

Keep source inventory, frame manifest, project/settings, processing fingerprints, render receipts, and QA results with the work. Use relative paths where practical; keep credentials out. Distinguish proxies, proofs, masters, and deliveries. Render to temporary/versioned paths and promote validated files.

## Encoding

Establish dimensions, aspect, rational frame rate, SDR/HDR, codec/bit depth, and destination requirements. 4K alone does not specify HDR or frame rate; 24 fps changes 30/60 fps camera cadence. Rebuild from originals rather than upscaling an old HD export. Explain unavoidable crop, temporal conversion, or lost camera metadata when relevant.

Inspect actual encoder help/hardware support and render a short sample. FFmpeg and GPU drivers can support different NVENC API versions: use a trusted compatible binary or CPU fallback instead of assuming a driver upgrade is needed. Verify option spelling on the installed binary. Check the sample's picture and metadata, not only its exit status.

Choose sufficient quality for the source/target and preserve a master when useful. Quality values are encoder-specific, not universal original-quality guarantees. Describe recompression accurately. Verify playback/container requirements; an available encoder does not establish browser compatibility.

## Verify the delivered artifact

1. Probe actual streams: dimensions, frame rate, frame count/duration, profile, pixel format/bit depth, color metadata, audio channels/rate. Decode the entire output to detect late errors and truncation.
2. Compare coverage/cuts with the manifest. Inspect first/middle/last of every shot and both sides of every cut. Distinguish intended fades/night subjects from unintended gaps or stabilization borders. Scene-change detection also responds to flashes and moving objects; it is not a cut oracle.
3. Review motion at playback speed where tools permit. Static sheets cannot establish smooth stabilization, cadence, or animation quality.
4. Verify intended soundtrack offset and alignment in several later windows. Check routing, duplicate tracks, clipping, gaps, and ending. Correlation establishes timing, not listening quality. Sample peak is not true peak or integrated loudness.
5. Derive audio length from frame count, rational frame rate, and sample rate, rounding deliberately when necessary. AAC priming/padding may change container duration; inspect decoded content before calling a small difference an edit error. Check the rendered fade's actual endpoint.
6. Inspect or reopen the saved project and confirm media/graphics dependencies remain available. A native backup with offline media is not self-contained.

For HDR, apply the color reference's pipeline checks. Report what was actually verified and any remaining playback/calibrated-display limitations. Tie compact evidence to the delivered file's fingerprint.
