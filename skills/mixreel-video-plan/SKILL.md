---
name: mixreel-video-plan
description: Group approved shots into coherent video requests, decide sparse keyframe needs and write model-specific motion prompts with ordered references. Use before keyframes and again to finalize prompts; never submits paid video jobs.
---

# Plan video generation and write prompts

## Inputs

Accept an approved script/scene with camera and action intent, reference observations and assigned media roles, target timing, existing assets and the selected provider's verified capabilities. Read [handoffs](../mixreel/references/handoffs.md), [planning](references/planning.md) and [provider contract](../mixreel/references/providers.md).

## Two useful entry points

Before new images, group connected shots by supported duration, reference limits, shared geography and retry scope. Decide the smallest sufficient set of new frames. Report editorial shot count, generation request count and new illustration count separately. Do not silently turn cuts into separate paid requests or stretch a fast action to a file's minimum duration.

With accepted assets, bind their real order and roles and finalize one prompt per approved group. Unsupported audio/video references must be reported and translated from observed evidence into text where possible. Placeholder bindings are a draft, not submit-ready prompts.

If the provider is unresolved, produce a provider-neutral group proposal and explicit capability questions. Do not invent model limits, picture labels, prices or API fields. Standalone prompt writing does not require unrelated film metadata.

## Model writing

Use only the selected verified prompt family. For [H3](references/prompt-minimax-h3.md), read [cinematic coverage](references/cinematic-coverage.md) and [H3 format](references/h3-format.md). H3 consumes the approved script directly. For [Seedance 2](references/prompt-seedance-2.md), respect the bundled single-setup scope; multi-shot capability needs separate evidence, not silent splitting.

Keep action, gaze, geography, rapid execution intervals, causal order and authored endings intact. Exact UI, brand marks and captions excluded by a model writing mode remain explicit edit-layer obligations; never delete them from the script or promise the model will render them faithfully.

## Deliver

Write `video-plan.md` with groups, split reasons, local timing, frame needs, capability evidence, reference inventory, per-request cost basis and prompt readiness. Add complete production fields to `plan.json` only when available; preserve version 1/2 compatibility. Use `<core>/scripts/validate_plan.py` on a complete production plan, not on a script-only artifact.

Return the selected model's exact structured prompt separately from the planning explanation. No paid submission or rewriting the accepted story. New creative cuts or conflicts return to the script decision rather than being hidden in the model prompt.
