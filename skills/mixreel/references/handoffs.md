# Stage artifacts and independent use

Install the whole collection so each specialist can resolve the common `mixreel` sibling. Invoke only the skill needed. The common directory is `<core>` in command examples; resolve it from the specialist's installed location, not the project's current working directory. Missing siblings are an installation problem, never permission to invent their rules.

## Accept existing work

Inspect supplied artifacts against the current request and reuse adequate ones regardless of who created them. Preserve source paths/IDs and accepted versions. A standalone task needs only its own meaningful inputs. Do not demand a full film plan to review an image or write a script.

| Stage | Minimum useful inputs | Reviewable output | Not required at this stage |
| --- | --- | --- | --- |
| Analysis | Accessible reference and analysis scope; target audio when relevant | `reference-analysis.md`, evidence locations, uncertainty, optional audio events | Product script, keyframes, provider |
| Script | Creative/advertiser requirements, reference evidence and relevant product/story facts | `script.md`, borrowing decisions, shot-level CG descriptions, sound plan and early feasibility | Paid account, generated assets, final verified request settings |
| Video plan | Accepted script/scene, reference roles, available assets, verified capabilities or explicit unknowns | `video-plan.md`, groups and frame needs; finalized prompts when bindings exist | New images when existing inputs suffice |
| Keyframes | Accepted visual requirement, necessary frame list, user-selected references and execution scope | `keyframes.md`, actual images or clearly labelled input plans, actual input manifest | Whole-film music/plan for a standalone image |
| Production | Accepted execution/edit plan, actual assets, capabilities and authority for the requested operations | Jobs, selected clips, edit records and video | New generation for edit-only requests |
| Review | Actual artifact and available target/evidence | `review.md`, located defects, repair destination and recheck status | New assets, paid API credentials |

These names are defaults for new project records, not requirements to rename existing files. The brief links each artifact's version, acceptance state and unresolved decisions. Do not duplicate authority or budgets across stage folders.

## From a script to a production plan

Keep a script proposal in Markdown while its production inputs are unresolved. The current `plan.json` versions 1 and 2 describe a music-based production/edit timeline, and version 3 adds generated or absent score, per-shot sound, edit-layer overlays and continuations; they are not the schema for every creative task. Do not put dummy music or generation groups into a script to pass `validate_plan.py`. For an authorized sound-only or other unsupported edit, record the real plan and use a suitable host editor rather than inventing a music track.

A full script already includes a sound proposal and a provisional feasibility check against known limits. Video planning verifies and finalizes these choices; it must not silently repair a structurally unworkable script after approval. An outline can defer that check explicitly.

When production planning is appropriate, preserve script shot IDs, source locators, action, timing and approved endings. Add actual reference inventory, generation groups, frame requirements and later clip ranges. Recheck timing against the chosen audio. Keep exact copy, UI, brand, dialogue and sound requirements in the linked script/edit-layer plan even when the model prompt or local renderer cannot express them.

Borrowing dimensions are creative decisions about the reference video. Provider input roles describe what each submitted asset supplies. They are different records: borrowing the source hook does not authorize using its frame as a style reference. Check both before submission.

## Ownership and change

The script skill owns the approved creative sequence. Video planning may propose production changes but cannot silently adopt them. Keyframes own artwork versions; production owns actual jobs/edits; review owns findings and rechecks. The coordinator selects the earliest affected stage. A specialist may perform a simple adjacent check, but must follow that stage's maintained rules rather than create a competing workflow.

For every handoff state what is actual, proposed, accepted, rejected or not checked. An agent check is not user approval. A simulated request is not a paid job. Missing evidence limits the conclusion; it does not automatically require rerunning all earlier stages.
