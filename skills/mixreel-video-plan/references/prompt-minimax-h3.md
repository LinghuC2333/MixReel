# MiniMax H3 CG Video Prompt

Adapted from the user-authorized source IDE prompt rules. This file writes prompts only; it does not submit generation jobs. Verify the selected endpoint with [the provider contract](../../mixreel/references/providers.md) before execution. Model IDs here identify source prompt families, not universal API identifiers.

Use this reference when the selected endpoint has been mapped to the MiniMax H3 prompt family (source ID `video-minimax-h3`). When the
active model is `video-seedance`, use `prompt-seedance-2.md` instead. Do
not run both prompt families for the same scene.

Turn one approved source scene description directly into the final MiniMax H3 full-reference prompt. This reference covers two authoring steps.

1. Direct the source event as a short cinematic sequence.
2. Encode that sequence in MiniMax H3 Ref2VA format.

Do not require or create an intermediate Seedance-style video description. Preserve the event, people, location, props, spatial relationships, gaze, action order, emotional reactions, and final image supplied by the source.

## Reference mode and approved cuts

Use this format only when the selected endpoint is verified to support this reference workflow. Prompt labels alone cannot activate API reference handling. A composition or ending reference is a soft guide unless the endpoint provides a verified strict frame constraint. Do not claim a guaranteed ending from prose alone.

An approved edit plan controls shot boundaries and music events. Write one prompt for the approved generation group, using request-local timing for its cuts and actions; do not create a paid call per shot. Bind video/audio references only through documented endpoint syntax, keeping picture labels for images. State when timing must be conveyed in text because a media input is unsupported. When a clip represents one approved continuous shot, keep it continuous; propose any new internal cuts before generation. Source-scene directing may suggest several shots during planning, but must not silently replace an already approved shot plan.

## Required inputs

- The approved source scene and ordered shot descriptions for one generation group.
- The ordered provider reference inventory. Each image entry must include its exact `<Picture N>` number and assigned role, such as character identity, outfit, environment, visual style or a frame anchor. Any supported video/audio inputs retain their documented identifiers and user-assigned roles separately.
- The selected visual style when no reference already supplies it.
- Any exact audible dialogue.
- The target aspect ratio when it materially affects composition.
- Any user-specified duration or duration ceiling. When neither is supplied, derive the duration from the finished shot plan.

Provider reference order is authoritative. Never derive picture numbers from prose order, filenames, URLs, or tag order. If the real order is unavailable, stop and report that H3 picture labels cannot be bound safely.

Character portraits, outfit anchors, sprites, backgrounds, and style images are reusable visual references. Treat them as `reference generation`. Do not call an image a first frame, keyframe, or last frame unless the host explicitly assigns that role.

## Workflow

### 1. Lock the story event

Extract the ordered visible beats before choosing shots. Track where every person and plot-critical prop begins, what changes, who sees what, and which image must end the clip. Do not move a person to another location, merge separate spaces, reverse cause and reaction, or invent a new event.

For every decisive physical action or prop state change, extract an action contract: the initial state, the contact or force that causes the change, the visible transition, and the resulting state. Give failure-prone actions such as cutting, locking, opening, handing over, mounting, or taking control enough screen time to complete. Describe positive physical geometry and causality instead of relying on words such as `really`, `actually`, or repeated prohibitions.

Extract the emotional contract as an arc: the opening emotional state, the source beat that changes or intensifies it, and the feeling left in the final image. A genuinely static mood may remain static when the source contains no emotional turn. Name the atmosphere once, then embody it through observable performance and filmmaking choices such as pace, held breath, gaze, body distance, hesitation, lighting, environmental motion, synchronous sound, or deliberate non-contact. Preserve the interactions established by the source.

When distance, consent, restraint, safety, or control carries the relationship beat, define its visual proof before directing: the exact hands, feet, gap, threshold, obstruction, or object ownership that must remain readable. Preserve that proof in the decisive shot and, when the source makes it the outcome, in the final image.

### 2. Design the coverage

Read [cinematic coverage](cinematic-coverage.md). Preserve every explicit cut or composition in the source. When the source leaves coverage open, choose the shots needed to make its existing action and reaction legible.

A clip may use one shot or several. Do not make a fixed composition the default, and do not add cuts merely to reach a quota. For two-person scenes, make the spatial relationship clear and use eyeline-matched over-the-shoulder shots, reverse shots, or reaction close-ups when the exchange depends on what each person sees or withholds. Use an environment shot or prop insert only when it establishes place, mood, transition, evidence, or a state change.

Each shot gets one coherent camera behavior. A static shot stays locked. A moving shot may use one principal movement such as a track, pan, tilt, or push-in. A later shot may choose a different camera behavior. Maintain screen direction, eyelines, prop continuity, and body positions across cuts.

Do not assign timestamps yet. First finish the complete shot plan and confirm that each shot has a necessary visual job.

Before timing the shots, identify where each action contract completes, where the emotional arc turns, and where the relationship proof becomes visible. A single shot may carry more than one job, but no required job may exist only in explanatory prose.

### 3. Derive the duration

Estimate how long each planned shot needs for its visible action, camera movement, dialogue, and reaction to read naturally. Read the timing guidance in [cinematic coverage](cinematic-coverage.md). Add the shot times and round up to a whole second. Use the verified provider profile to establish supported durations. Round to a supported duration that allows the action to finish; handle longer estimates with the fitting rule below rather than silently truncating them.

Keep brief action execution separate from setup and reaction time, even when the requested file must meet an endpoint minimum. Do not stretch a simple event to a familiar default. Do not compress a complex event merely to reuse another CG's duration. If the honest estimate exceeds the verified maximum duration, first remove decorative coverage or merge shots that remain legible. If the source event still cannot fit, stop and report that it requires more than one clip rather than dropping story beats.

When the user supplies an exact duration, fit the coverage to that duration without damaging the event. Report a conflict if the required action cannot read inside it. When the user supplies a ceiling, choose the shortest natural duration at or below it.

After selecting the duration, assign every later shot a strictly increasing cut time inside it. Leave enough time for the final action or reaction to complete before the clip ends.

### 4. Bind references

Resolve each tagged character, background, prop, and style anchor to a stable `<Subject N>`. Cite the exact `<Picture N>` source in its definition. Preserve only the roles assigned to each reference. An identity-only face reference does not supply wardrobe. For an approved wardrobe change, bind the selected outfit separately and preserve the approved action, pose, gaze, and expression.

Keep visual appearance bound to references. Do not invent hair, facial features, clothing, architecture, colors, or materials that the inventory should supply. Give every plot-critical prop an explicit position and state change in the shot where it matters. Do not name a prop or person in a shot where it must stay out of frame, even in a negative sentence; the name tends to put it in the picture. Describe the gaze direction or screen position instead, and name the object only in shots that show it.

### 5. Write the H3 prompt

Read [H3 format](h3-format.md) and write the six sections in its exact order. Write prompt prose in English while preserving dialogue and visible source text in their original language.

Use `[Shot 1]` without a timestamp. Start every later shot with `[Shot N] At MM:SS.mmm, ...`. Put exact spoken words inside `<d>[Language] ...</d>` and assign stable `(S1)`, `(S2)`, and later speaker IDs by the order of actual vocal events. Do not invent dialogue.

Write synchronous ambience, action sounds, and non-verbal human sounds. Follow the approved sound plan. Use `non_diegetic_music` for requested model-composed score only when native music output is verified; use `N/A` for no generated score or score added in editing. Do not erase the script's music request through a template default.

Keep the prompt compact. Use `summary` for one short sentence, `retention_analysis` for reference fidelity, and `detailed_description` for the actual staging. Do not restate the same appearance, geography, mood, or prohibition across all three sections. When shortening, remove repeated style language and explanation before cutting story beats, action causality, emotional change, spatial proof, dialogue, or the authored final image.

### 6. Audit the result

Before returning the prompt, verify all of the following:

- The shot sequence preserves every source beat and the final image.
- Every decisive action shows enough initial state, contact or force, transition, and result to read as completed.
- The emotional arc has a clear opening state, turning or intensifying beat when the source supplies one, and final residue, all embodied through concrete visual or audible cues.
- Any required boundary, restraint, safety, distance, or control remains visible as physical evidence rather than existing only as an instruction.
- Cuts help reveal action, reaction, space, mood, or information.
- Two-person geography and eyelines remain coherent.
- Gaze targets are explicit during turns, looks back and shifts of attention, including when camera movement reveals a face.
- Every reference label matches the provider inventory and keeps one meaning.
- Every critical prop has continuous position, ownership, and state.
- No object or person that must stay out of a shot is named in that shot.
- Cut times increase and remain inside the target duration.
- Dialogue, sound, and visible text are synchronized and not invented.
- The prompt contains no unresolved source tags, URLs, local paths, model settings, executor commands, subtitles, logos, watermarks, or fade to black.
- The complete prompt fits the verified endpoint character limit. The source IDE used a 4000-character limit; this is historical integration evidence, not a universal H3 limit.

## Output

Return exactly one valid JSON object and no Markdown or commentary. `duration` is the selected whole number of seconds. The `description` value contains the complete six-section prompt. Do not repeat the duration inside the H3 prompt body.

```json
{"duration":10,"description":"subject_definitions:\n...\n\nsummary:\n...\n\nretention_analysis:\n...\n\ndetailed_description:\n...\n\noverall_soundscape:\n...\n\nnon_diegetic_music:\nN/A"}
```

This reference authors a prompt only. It must not call `videoctl`, a gateway, a provider API, media upload, or any paid generation tool. It must not edit the approved source scene description.
