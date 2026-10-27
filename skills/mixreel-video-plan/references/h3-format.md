# MiniMax H3 Ref2VA contract

Adapted from the user-authorized source IDE prompt rules. This file writes prompts only; it does not submit generation jobs. Verify the selected endpoint with [the provider contract](../../mixreel/references/providers.md) before execution. Model IDs here identify source prompt families, not universal API identifiers.

Use this contract after the CG has been divided into a coherent shot sequence.

## Exact section order

The prompt contains these six fields in this order:

```text
subject_definitions:
...

summary:
...

retention_analysis:
...

detailed_description:
...

overall_soundscape:
...

non_diegetic_music:
N/A
```

## Reference labels

`<Subject N>` names reusable visible content such as a person, environment, prop, or visual style. Define each subject once and keep its meaning stable.

`<Picture N>` identifies an input image by its actual provider order. When an image supplies identity, outfit, environment, or style, cite it inside the corresponding subject definition. One picture may supply several subjects, and one subject may combine several pictures when each role is stated.

Create a standalone `<Picture N>` definition only when the image is an exact first frame, keyframe, last frame, edited frame, storyboard, or composition anchor. Ordinary identity and environment references do not become frame anchors.

## `subject_definitions`

Give every reused person, environment, prop, style, standalone picture, video, or audio reference one clear definition. When a visual style is a hard requirement, define it as the first subject so the prompt opens with it; name its source references and the motion texture it implies, and render every shot in it. State which asset supplies it and what must remain stable. Do not invent visual traits absent from the inventory.

Example:

```text
<Subject 1> is the courier as shown in <Picture 1>; preserve her identity, current outfit, proportions, and stylized rendering while changing only pose, gaze, expression, and action.
```

## `summary`

Begin with `[reference generation]` for ordinary reference-image generation. Summarize the target event, shot flow, and main reference relationships in one short English paragraph. Use only labels already defined.

Use other task types only when the input genuinely requires them:

- `keyframe completion` for an exact target frame anchor.
- `video editing` when an existing source video is directly modified.
- `video continuation` when the target continues an existing video.
- `audio reuse` when the same audio signal is copied.
- `audio reference` when timbre, rhythm, voice, or sound texture guides new audio.

Combine real relationships with ` + ` inside one bracketed prefix.

## `retention_analysis`

Write one line for every defined reference label. Name the shots where visible subjects appear.

Use only the matching relationship markers:

- `fully_preserved` when the defined identity, outfit, environment, prop, or style role remains intact.
- `partially_preserved` when part of that defined role changes or appears only partly.
- `attribute_transfer` when referenced traits move to another identifiable target.
- `weak_reference` when only broad style, atmosphere, composition, or category remains.

New actions required by the target scene do not count as lost identity fidelity.

## `detailed_description`

Open with one or two English sentences establishing visual style. Then write the video in playback order.

- `[Shot 1]` has no timestamp.
- Every later shot begins `[Shot N] At MM:SS.mmm, ...` with a strictly increasing cut time inside the requested duration.
- For every shot, describe composition, visible subjects, environment, action, camera behavior, synchronous sound, and continuity from the prior shot.
- Insert each reference label where its role first becomes visible and wherever a concrete frame, video, or audio relationship applies.
- End on the source's required final image without a fade.

Keep speaker IDs stable by the order of actual vocal events. A referenced speaking character appears as `<Subject N> (S1)`. Put exact dialogue inside `<d>[Language] ...</d>`. Preserve original wording and language. Do not turn thoughts, narration, or emotional meaning into dialogue.

## Sound fields

Keep shot-synchronized dialogue and sound events in `detailed_description`.

`overall_soundscape` summarizes continuous ambience, physical action sounds, and non-verbal human sounds. Do not repeat dialogue there.

`non_diegetic_music` describes audience-only score. Use `N/A` when the approved plan calls for no generated score, including music added separately in editing. If the approved script requests model-composed music and the verified endpoint supports it, write its requested cue progression, texture, accents and ending here. Do not silently replace an authored score with `N/A`; unsupported audio needs an explicit production alternative. Separate generated clips require a documented continuity or musical transition plan.

## Prompt exclusions

The finished prompt body contains no raw `@character` or `@bg` tags, URLs, local paths, YAML, model name, duration field, ratio field, resolution field, request schema, subtitles, logos, watermark, or executor command. The outer skill result carries the selected integer `duration`; that value controls shot timing but is not repeated inside the six-section prompt body.
