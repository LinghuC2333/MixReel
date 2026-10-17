# Animate and cut to the actual result

## Shot motion

Read the approved shot plan and reference inventory before each prompt. Preserve the principal camera behavior, gaze targets, visible action sequence and final state. Specify subjects by stable roles and exact reference order rather than vague pronouns. Do not substitute looking at the lens for looking toward another character.

Match the reference's kind of motion. For illustrated tableaux, camera travel, foreground parallax, breathing and cloth motion may be sufficient. For a confrontation, contact, force and reaction must be visible. A camera move should reveal information, alter distance or emphasize power; decorative movement in every shot is not a quality criterion.

Prefer one approved shot per generated clip when edit timing matters. Multi-shot generation is an explicit option when the selected model supports it and its cuts can be reviewed. Do not turn a shot into several unplanned angles.

## Capability and reference checks

Before submission read the selected provider profile and current documentation. Determine whether strict start/end frames and style references can coexist. If not, compare the trade-off and choose a supported mode; never silently discard a reference. For reference-only mode describe opening and ending images as requested anchors, and inspect whether the video actually follows them.

When preserving a stylized look, provide a supported style conditioning mechanism and carry the approved rendering description into each clip. If unavailable, test a short sample or report the limitation before a batch. Provider support and practical quality are separate questions.

Allow edit handles around essential actions where the model's timing is unreliable. Choose length from readable action plus tested timing tolerance, subject to supported durations and budget. Do not impose the same seconds or a historic delay on all models. If complexity exceeds the slot, simplify or split before paying.

A resolution or motion-risk comparison is a paid experiment. State its cost and use existing authorization or obtain the missing authorization. Compare one representative shot before multiplying the cheaper option.

## Inspect and select

Watch the actual returned clips, including beginning and end. Check subject identity, rendering, contact, direction, gaze, final state and camera movement. A finished provider job can still be unusable.

Use `python3 scripts/media_inspect.py motion CLIP OUTPUT.json` to locate candidate visual changes. Frame-difference peaks can be a camera move, flash or defect. Inspect surrounding frames to identify the intended narrative accent. Record actual event time and confidence; prompt timestamps are not observations.

## Edit plan

Record each clip's source in-point, source duration, output interval, playback speed and transition. For a clip with speed `s`, source accent `a`, target accent `T` and timeline start `t`, use `clip_in = a - s * (T - t)`. Then verify the selected range exists. A negative in-point means the edit needs changing, not silent clamping.

Use cuts and reveals on selected musical events. Preserve readable reactions and a coherent ending; not every beat requires an event. Mark intentional off-beat cuts. Dissolves consume overlap and require handles; model them explicitly so they do not shorten the film unexpectedly. Retiming limits follow the scene and acceptable motion, not a fixed universal percentage. Keep synchronous sound in time when retiming or omit unusable sound deliberately.

Frame holds such as twelve distinct drawings per second played at twenty-four frames per second can produce a hand-drawn cadence. Offer or use this according to recorded preference. Compare motion and cut timing after applying it. It is an editing treatment, not a reason to regenerate already acceptable footage.

## Deliver

Render a quality master and a mobile-friendly preview with an editing tool available in the host. Verify duration, frame size, aspect ratio, frame rate, audio coverage, silence, clipping, cut boundaries and encoding quality. Use `media_inspect.py audio` on the final output as a diagnostic, then listen; intended silence should not be classified as an automatic defect.

Watch once without explanatory notes, then with music. Report unresolved creative defects separately from technical checks. Provide the requested delivery location only under the user's authorization. Include the plan, accepted references, export settings and costs with estimates visibly separated from actual billed amounts.
