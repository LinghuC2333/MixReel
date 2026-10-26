# Animate and cut to the actual result

## Plan generation requests before images

Keep editorial shots separate from generation requests. Default to one request for the whole generated sequence when it fits the verified maximum duration and prompt limit, including multiple approved shots when supported. Group connected action and shared geography together. Split only for a documented reason such as endpoint duration/reference limits, a scene change, incompatible inputs or a lower expected rework cost. In reference mode, keyframes and reference images are soft guides, so wanting a separate opening anchor for each part is not a reason to split by itself. Do not assume grouping guarantees continuity.

Before producing keyframes, record the ordered shot IDs, requested duration, continuity requirements, references and grouping reason in `generation_groups` as described in [Project records](../../mixreel/references/records.md). Keep each shot's own action and camera plan. Choose the smallest sufficient set of reviewed images to establish identity, wardrobe, spatial layout or a critical state that the script and other references cannot reliably convey. Reuse suitable accepted assets. A shot can share a keyframe or need no new image; do not generate a starting and ending frame for every cut.

Use the approved script and shot sequence as the main direction. When a [spatial previs](../../mixreel-script/references/previs.md) exists, its storyboard sheet can carry staging and camera direction for every shot in one ordered image. Add reference video for the user-assigned composition or motion role, reference audio for approved timing or sound, and style/character images only in their recorded roles. A style image or clip that shows a person can transfer that person's identity; prefer faceless style material or an approved project frame, and check every character after generation. Verify that the endpoint accepts these media types together, including durations, counts, ordering and sound behavior. If a reference cannot be submitted, record the limitation and translate its observed timing or motion into text; do not pretend that the model received the media or silently switch providers. Music used for timing need not become generated background sound. Follow the script's decision on where the final score comes from; when edit-layer music will replace the model's audio, prompt for dialogue and sound without score.

Compare grouping alternatives using the actual provider's minimum billable duration, duration increments, resolution and expected retry scope. Show requested and estimated billable seconds per request, total quoted/estimated cost and what a rejected sequence would require regenerating. Keep unknown prices or retry rates unknown; do not promise savings from fewer calls alone. Reserve and reconcile each generation request once, even when its output supplies several timeline shots.

Separate the duration of an action from the duration of its generated file. Give fast actions a brief execution interval, clear contact and a readable aftermath within the sequence; do not stretch them to the provider's minimum length. Use any necessary extra footage for approved setup, reaction or removable handles. Do not invent filler actions, default slow motion or blanket speed-up. Translate the shot times and musical accents to request-local times, with the intended cuts and action speeds explicit.

## Continue past the duration limit

When the generated sequence exceeds the verified maximum, generate the first request at that maximum and continue from its accepted result. Use the final seconds of that clip as the next request's reference video, plus its audio as reference audio when score or ambience must carry on, and write the new prompt as a continuation of that clip. Verify that the endpoint accepts these references together. Independent segments cannot share motion, sound or music, so use them only when continuation is unsupported.

Place each continuation boundary at a planned cut, so the continuation opens on a new camera setup. A continuation that resumes the same shot tends to reframe slightly, which reads as a jump. Inspect the seam, discard repeated or jumping head frames and record the source ranges actually used.

## Shot motion

Read the approved shot plan and reference inventory before each prompt. Preserve the principal camera behavior, gaze targets, visible action sequence and final state. Specify subjects by stable roles and exact reference order rather than vague pronouns. Do not substitute looking at the lens for looking toward another character.

Choose camera and subject movement from the approved sequence and the reference observations. Describe what changes during the shot and what the viewer should notice as it unfolds.

Plan the approved group as one request using the selected endpoint's verified multi-shot format. If the available authoring mode handles only one camera setup, retain it for an appropriate single-shot group or resolve the capability mismatch before submission. Do not silently break a group into per-shot paid calls or introduce unapproved angles.

## Capability and reference checks

Before submission read the selected provider profile and current documentation. Determine whether strict start/end frames and style references can coexist. If not, compare the trade-off and choose a supported mode; never silently discard a reference. For reference-only mode describe opening and ending images as requested anchors, and inspect whether the video actually follows them.

When preserving a stylized look, provide a supported style conditioning mechanism and carry the approved rendering description into each clip. If unavailable, propose an authorized representative test or report the limitation before a batch; execution belongs to production. Provider support and practical quality are separate questions.

Allow edit handles around essential actions where the model's timing is unreliable. Choose length from readable action plus tested timing tolerance, subject to supported durations and budget. Do not impose the same seconds or a historic delay on all models. If complexity exceeds the slot, simplify or split before paying.

A resolution or motion-risk comparison is a paid experiment. Propose it only when the choice cannot be made otherwise, and run it only when the user asks for that comparison and its cost. Compare one representative shot before multiplying the cheaper option.

