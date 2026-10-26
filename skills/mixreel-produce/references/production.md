# Edit and deliver video

## Edit plan

Keep a satisfactory generated sequence intact wherever its actual timing fits. For timeline shots drawn from one result, use the same source asset with observed in-points and its full duration; do not regenerate those shots merely to create separate files. Avoid replaying or skipping action at shared-source joins. Record each clip's source in-point, source duration, output interval, playback speed and transition. For a clip with speed `s`, source accent `a`, target accent `T` and timeline start `t`, use `clip_in = a - s * (T - t)`. Then verify the selected range exists. A negative in-point means the edit needs changing, not silent clamping.

Use cuts and reveals on selected musical events. Preserve readable reactions and a coherent ending; not every beat requires an event. Mark intentional off-beat cuts. Dissolves consume overlap and require handles; model them explicitly so they do not shorten the film unexpectedly. Retiming limits follow the scene and acceptable motion, not a fixed universal percentage. Keep synchronous sound in time when retiming or omit unusable sound deliberately.

Composite exact UI, captions and brand layers over the interval reserved for them. Keep live footage under partial overlays and use a held or blurred frame only where the product screen covers the picture. Keep score and sound continuous through the overlay; interface sounds sit on top.

Frame holds such as twelve distinct drawings per second played at twenty-four frames per second can produce a hand-drawn cadence. Offer or use this according to recorded preference. Compare motion and cut timing after applying it. It is an editing treatment, not a reason to regenerate already acceptable footage.

## Deliver

Render a quality master and a mobile-friendly preview. Once every shot has `clip {asset, in, duration, speed}`, `python3 <core>/scripts/render_edit.py PLAN MASTER --preview PREVIEW [--holds 12]` renders the cut, frame holds, dissolves and music from the plan; any other host editing tool is equally valid. Verify duration, frame size, aspect ratio, frame rate, audio coverage, silence, clipping, cut boundaries and encoding quality. Use `media_inspect.py audio` on the final output as a diagnostic, then listen; intended silence should not be classified as an automatic defect.

The helper outputs music only and discards source-clip audio. It adds a 0.3-second music fade-out and sharpens clips narrower than the output width; review those treatments before delivery. Use another editing tool when synchronous sound or different finishing controls are required.

Watch once without explanatory notes, then with music. Report unresolved creative defects separately from technical checks. Provide the requested delivery location only under the user's authorization. Include the plan, accepted references, export settings and costs with estimates visibly separated from actual billed amounts.
