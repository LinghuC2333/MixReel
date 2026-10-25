# Animate and cut to the actual result

## Plan generation requests before images

Keep editorial shots separate from generation requests. Prefer one coherent sequence per request, including multiple approved shots when supported, and consider the whole short when it fits. Group connected action and shared geography together. Split only for a documented reason such as endpoint duration/reference limits, a scene change, incompatible inputs or a lower expected rework cost. Do not force the whole film into one request or assume grouping guarantees continuity.

Before producing keyframes, record the ordered shot IDs, requested duration, continuity requirements, references and grouping reason in `generation_groups` as described in [Project records](records.md). Keep each shot's own action and camera plan. Choose the smallest sufficient set of reviewed images to establish identity, wardrobe, spatial layout or a critical state that the script and other references cannot reliably convey. Reuse suitable accepted assets. A shot can share a keyframe or need no new image; do not generate a starting and ending frame for every cut.

Use the approved script and shot sequence as the main direction. Add reference video for the user-assigned composition or motion role, reference audio for approved timing or sound, and style/character images only in their recorded roles. Verify that the endpoint accepts these media types together, including durations, counts, ordering and sound behavior. If a reference cannot be submitted, record the limitation and translate its observed timing or motion into text; do not pretend that the model received the media or silently switch providers. Music used for timing need not become generated background sound.

Compare grouping alternatives using the actual provider's minimum billable duration, duration increments, resolution and expected retry scope. Show requested and estimated billable seconds per request, total quoted/estimated cost and what a rejected sequence would require regenerating. Keep unknown prices or retry rates unknown; do not promise savings from fewer calls alone. Reserve and reconcile each generation request once, even when its output supplies several timeline shots.

Separate the duration of an action from the duration of its generated file. Give fast actions a brief execution interval, clear contact and a readable aftermath within the sequence; do not stretch them to the provider's minimum length. Use any necessary extra footage for approved setup, reaction or removable handles. Do not invent filler actions, default slow motion or blanket speed-up. Translate the shot times and musical accents to request-local times, with the intended cuts and action speeds explicit.

## Shot motion

Read the approved shot plan and reference inventory before each prompt. Preserve the principal camera behavior, gaze targets, visible action sequence and final state. Specify subjects by stable roles and exact reference order rather than vague pronouns. Do not substitute looking at the lens for looking toward another character.

Choose camera and subject movement from the approved sequence and the reference observations. Describe what changes during the shot and what the viewer should notice as it unfolds.

Generate the approved group as one request using the selected endpoint's verified multi-shot format. If the available authoring mode handles only one camera setup, retain it for an appropriate single-shot group or resolve the capability mismatch before submission. Do not silently break a group into per-shot paid calls or introduce unapproved angles.

## Capability and reference checks

Before submission read the selected provider profile and current documentation. Determine whether strict start/end frames and style references can coexist. If not, compare the trade-off and choose a supported mode; never silently discard a reference. For reference-only mode describe opening and ending images as requested anchors, and inspect whether the video actually follows them.

When preserving a stylized look, provide a supported style conditioning mechanism and carry the approved rendering description into each clip. If unavailable, test a short sample or report the limitation before a batch. Provider support and practical quality are separate questions.

Allow edit handles around essential actions where the model's timing is unreliable. Choose length from readable action plus tested timing tolerance, subject to supported durations and budget. Do not impose the same seconds or a historic delay on all models. If complexity exceeds the slot, simplify or split before paying.

A resolution or motion-risk comparison is a paid experiment. State its cost and use existing authorization or obtain the missing authorization. Compare one representative shot before multiplying the cheaper option.

## Inspect and select

Watch each returned sequence through its internal cuts before selecting footage. Check that positions, screen direction, contacts and action speed remain continuous and the planned events are present. Compare observed cuts and accents with the request-local plan; prompt timestamps are not proof of frame-accurate timing. Watch the actual returned clips, including beginning and end. Check subject identity, rendering, contact, direction, gaze, final state and camera movement. Inspect gaze throughout each clip against the approved targets, especially during turns, looks back and camera moves that reveal a face. If a character unexpectedly looks into the lens, first try adjusting the in-point and playback speed to exclude that interval while preserving the required action and timing; regenerate only if editing cannot avoid it. A finished provider job can still be unusable.

Use `python3 scripts/media_inspect.py motion CLIP OUTPUT.json` to locate candidate visual changes. Frame-difference peaks can be a camera move, flash or defect. Inspect surrounding frames to identify the intended narrative accent. Record actual event time and confidence; prompt timestamps are not observations.

## Edit plan

Keep a satisfactory generated sequence intact wherever its actual timing fits. For timeline shots drawn from one result, use the same source asset with observed in-points and its full duration; do not regenerate those shots merely to create separate files. Avoid replaying or skipping action at shared-source joins. Record each clip's source in-point, source duration, output interval, playback speed and transition. For a clip with speed `s`, source accent `a`, target accent `T` and timeline start `t`, use `clip_in = a - s * (T - t)`. Then verify the selected range exists. A negative in-point means the edit needs changing, not silent clamping.

Use cuts and reveals on selected musical events. Preserve readable reactions and a coherent ending; not every beat requires an event. Mark intentional off-beat cuts. Dissolves consume overlap and require handles; model them explicitly so they do not shorten the film unexpectedly. Retiming limits follow the scene and acceptable motion, not a fixed universal percentage. Keep synchronous sound in time when retiming or omit unusable sound deliberately.

Frame holds such as twelve distinct drawings per second played at twenty-four frames per second can produce a hand-drawn cadence. Offer or use this according to recorded preference. Compare motion and cut timing after applying it. It is an editing treatment, not a reason to regenerate already acceptable footage.

## Deliver

Render a quality master and a mobile-friendly preview. Once every shot has `clip {asset, in, duration, speed}`, `python3 scripts/render_edit.py PLAN MASTER --preview PREVIEW [--holds 12]` renders the cut, frame holds, dissolves and music from the plan; any other host editing tool is equally valid. Verify duration, frame size, aspect ratio, frame rate, audio coverage, silence, clipping, cut boundaries and encoding quality. Use `media_inspect.py audio` on the final output as a diagnostic, then listen; intended silence should not be classified as an automatic defect.

The helper outputs music only and discards source-clip audio. It adds a 0.3-second music fade-out and sharpens clips narrower than the output width; review those treatments before delivery. Use another editing tool when synchronous sound or different finishing controls are required.

Watch once without explanatory notes, then with music. Report unresolved creative defects separately from technical checks. Provide the requested delivery location only under the user's authorization. Include the plan, accepted references, export settings and costs with estimates visibly separated from actual billed amounts.
