# Color and stabilization

## Establish the pipeline

Probe sources and confirm editor input, working, and output spaces. iPhone footage may be BT.2020 HLG, Dolby Vision, SDR, or another mode; device name does not establish transfer function. Photos may be sRGB, Display P3, or HDR. Convert profiles deliberately; SDR graphics in HDR need explicit luminance interpretation.

Separate technical normalization from creative grading. Match exposure and white balance per shot, protect highlights, then shape contrast and saturation. Compare faces, daylight, skies/foliage, night streets, and neon/stages. Preserve motivated colored light without clipping entire scenes. Favor controlled chroma, a gentle shoulder, and believable shadows over a blanket teal-orange LUT. LUTs must match the input domain.

For oversharp phone footage, remove added sharpening first. Modest high-resolution softening may help; judge at output size rather than imposing a fixed blur radius. Grain is optional and should survive compression without obscuring the picture.

## HDR invariants

HDR delivery requires HDR pixel processing throughout, sufficient intermediate precision, and matching metadata. Tagging SDR pixels as HLG does not restore HDR. A 10-bit output container cannot prove an earlier filter avoided 8-bit quantization.

For HLG, retain high-bit-depth or floating-point processing and appropriate BT.2020/HLG interpretation through grading/export. Inspect filters' negotiated pixel formats. One tested vidstab path used 8-bit pictures internally despite a 10-bit final codec: audit the installed pipeline rather than assuming stabilization preserves precision.

Use verified high-quality mezzanines such as DNxHR HQX or suitable ProRes, and a supported 10-bit delivery such as HEVC Main 10. Verify actual pixel format, primaries, transfer, matrix, range, and frame rate. Some encoders reset tags: metadata-only remuxing is appropriate only when independently established pixel semantics are correct. Edited HLG generally does not retain original camera Dolby Vision dynamic metadata; describe delivery accurately.

Map graphics to appropriate HDR diffuse white instead of peak code value. Approximately 0.75 HLG signal served as reference white in one pipeline while 1.0 produced peak highlights; verify the actual project/display transform before applying values. Isolate or duplicate the project before global color changes that would alter old SDR timelines.

Use explicitly tone-mapped SDR contact sheets on ordinary displays. They support composition and relative grading, not calibrated HDR assessment. When an accidental color transform is suspected, compare representative exported pixels against the intended processing as well as inspecting metadata.

## Stabilization

Distinguish shake from deliberate pans, vehicles, and foreground movement. Test difficult shots before processing everything. Use conservative translation/rotation smoothing, bounded corrections, and a fixed edge-safe crop when practical. Strong warps and pumping zoom can look worse than the original. Rigid stabilization does not necessarily fix rolling shutter.

One high-precision route estimates movement on small grayscale proxies with feature tracking and robust rigid fitting, smooths the trajectory, then transforms the original high-bit-depth pixels. Proxy precision is acceptable for estimation; proxy pictures must not become finishing sources. Mask moving subjects that dominate tracking, such as a train beneath a stationary ceiling. Verify intermediate precision and color after transformation.

Keep trim handles for smoothing when available. Use rational timing and clamp tiny near-zero roundoff before flooring; a negative epsilon otherwise becomes a negative frame handle. Inspect shot ends and difficult motion for borders, wobble, drift, excess crop, and lost subjects. Fingerprint source, trim, processing settings, and tool version before reusing intermediates.
