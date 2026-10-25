# Make the proposal visually reviewable

## Review format

For a script proposal, show the visible sequence with target timing or provisional pacing, image/action/camera, exact copy/dialogue, sound/music and product/brand treatment when relevant. Include source locators and selected reference functions. Use the [script template](../assets/SCRIPT.template.md) as needed.

A script-only request does not require generation groups, new images or a selected model. After the creative plan is accepted, [video planning](../../mixreel-video-plan/SKILL.md) assigns groups and necessary frame counts before illustrations. Preserve shot IDs across that handoff. Camera cuts do not imply separate calls.

## Editable scene description contract

Serialize each scene description as `{"description":"..."}` when a tool needs structured input. The prose contains the following information in natural order.

- Establish the view and subjects' physical relationship, including what is outside the frame.
- Give the camera one principal behavior and a destination. For a fixed camera, explicitly prohibit dolly, zoom and pan. This wording applies only when the shot is intentionally fixed.
- Describe observable actions and reactions in their causal order. For a risky action, make the starting state, contact or force, transition and resulting state visible.
- State the ending composition and what must remain readable there. Give plot-critical props their own sentences.
- Specify synchronous environment and action sound when relevant. Record score and edit-layer audio separately from scene sound; preserve the user-selected treatment.

Keep this description free of model settings, duration ceilings, reference lists, URLs, style headers, readable overlays and fade-to-black instructions. Do not repeat wardrobe already supplied by the visual references. Put technical timing and appearance bindings in the adjacent fields. This exclusion applies only to the generation-facing scene field. Put approved captions, titles, UI, brand marks and ending treatments in the script and edit-layer fields so they remain visible to production.

The editable scene description is a review artifact. H3 may use several approved shots and reads the original approved scene plus shot plan directly; it must not inherit the one-setup Seedance output as its source. Read the selected [Seedance 2](../../mixreel-video-plan/references/prompt-seedance-2.md) or [H3](../../mixreel-video-plan/references/prompt-minimax-h3.md) authoring rules only after model selection.

The provider prompt is a separate rendering of the approved generation group, combining its ordered shot descriptions and continuity requirements. It can add ordered reference bindings, supported timing hints and locked style instructions. It must preserve action, gaze, causality and the authored ending. Never let a provider adapter rewrite the story to fit a familiar prompt template.

## Continuity and variation

Track character positions, screen direction, eye lines, prop ownership, injuries, wardrobe, environment and time of day across cuts. Keep each character's user-selected outfit consistent within a continuous scene using the wardrobe-reference rules in [Images](../../mixreel-keyframes/references/images.md). Write the visual cause of each meaningful change. A change of angle is legitimate when geography remains understandable; no automatic ban on repeated angles or static shots.

Ask what new information each shot adds. Use a wide view for scale, an over-shoulder view for what someone sees, an insert for evidence, or a close-up for a readable reaction. These are choices justified by the scene, not a checklist that forces every type into every film.

Choose camera movement or stillness for what the viewer needs to discover and how the action develops. Do not default all shots to a locked camera merely because it is easier to describe, or add motion only to make the list more varied. Record the purpose of a consequential camera choice in the production notes.

Check that the starting state, action and ending can follow one another within the slot. Adjust staging or timing before generation when they cannot.

A montage can connect non-consecutive source moments through a deliberate emotional progression. Label this structure so omitted causality is intentional. A continuous scene requires continuous geography and action.

## Approval scope

Present the actual visual plan before illustration. Record the artifact revision and user response. Changing the story, emotional premise or major staging invalidates dependent review. Correcting a typo does not. If the user asks only for a proposal, stop after delivering it; generation remains a later task.
