---
name: mixreel-keyframes
description: Create or locally repair the necessary illustration keyframes using the GPT blocking, Ideogram completion and GPT repair workflow. Use for character/style-consistent artwork with explicit reference roles; accepts existing shot and frame requirements.
---

# Make necessary keyframes

## Inputs

Read the approved shot or visual request, necessary-keyframe requirements, available composition/character/style/wardrobe assets, provider access and applicable budget. Read [handoffs](../mixreel/references/handoffs.md) and [images](references/images.md). A standalone illustration request needs its own visual specification, not an invented whole-film plan.

For a video project, generation planning determines which new frames are actually necessary before this stage. Reuse suitable assets and share frames where sufficient. A user-requested standalone image remains valid without a video group.

## Execute and inspect

Follow the documented four stages: select one composition reference, two-image GPT blocking draft, Ideogram completion, localized GPT repair. Keep the direct-reference-frame branch conditional as documented. Preserve the user-confirmed role of every input; appearance choices remain the user's, including character reference format and wardrobe.

Read [providers](../mixreel/references/providers.md), [local configuration](../mixreel/references/local-config.md) and [execution](../mixreel/references/execution.md) before paid calls. Resolve actual model/tool identity and supported edit fields. Do not substitute providers silently. Planning or mock mode produces a manifest, never a claimed generated image.

Check composition, identity, style, clothing, gaze, anatomy and regions outside each repair. Character/style drift returns to completion with original inputs; localized repair cannot redesign the character. Use [diagnosis](../mixreel-review/references/diagnosis.md) for retry decisions.

## Deliver

Return the requested images, stage/version records, the ordered actual-input manifest, comparison findings and costs. Link them from `keyframes.md` in the private project. Record pending/accepted/rejected versions distinctly. Hand off the actual selected assets to video planning; no automatic video submission.
