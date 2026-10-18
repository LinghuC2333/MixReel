---
name: reference-replica-video
description: Use when adapting a reference video's emotional effect and filmmaking to a new story or IP with target music, or revising an existing reference-led short-video project. Also applies to proposal-only and storyboard-only requests.
---

# Reference Replica Video

Adapt the reference's audience experience to the user's story, music and visual identity. Deliver only the requested stage. A proposal request does not authorize media generation.

## Resume before planning

Read the project's `BRIEF.md`, `plan.json`, approved artifacts and job journal if present. Match the current request to the earliest affected stage. Reuse accepted decisions; inspect old assets before reusing them. If records conflict, the user's latest instruction wins. Record the change and invalidate only dependent decisions.

For a new project, record the reference, target music or excerpt, story sources, audience, deliverable and spending authority in `BRIEF.md`. Ask only consequential missing questions. Choose own-IP style or reference-video style with the user if unspecified. Preserve an already stated choice. Store private work outside this skill's source tree.

## Read only the stage you need

| Current need | Read | Produce |
|---|---|---|
| Understand a reference and target music | [Analysis](references/analysis.md) | Shot evidence, music events, uncertainty |
| Select story or prepare a proposal | [Story](references/story.md) and [Storyboard](references/storyboard.md) | Source-grounded candidates and a timed visual plan |
| Choose style or make/edit illustrations | [Images](references/images.md) | Approved style and identity references, reviewed keyframes |
| Animate, cut or export | [Motion and editing](references/motion-edit.md) | Reviewed motion, beat-aligned edit, delivery checks |
| Install or locate model credentials | [Local configuration](references/local-config.md) | Private provider profiles and credential locations |
| Write a Seedance 2 video prompt | [Seedance 2](references/prompt-seedance-2.md) | Compact scene description for the selected model |
| Write an H3 video prompt | [H3 authoring](references/prompt-minimax-h3.md), [H3 format](references/h3-format.md) and [Cinematic coverage](references/cinematic-coverage.md) | Reference-bound prompt and supported duration |
| Configure tools, spend or resume jobs | [Execution](references/execution.md) and [Provider contract](references/providers.md) | Verified capability profile and reconciled journal |
| Recover from a quality problem | [Diagnosis](references/diagnosis.md) | Narrow repair and affected-artifact list |

Select only the video prompt family verified for the chosen endpoint. H3 consumes the approved source scene directly, never a Seedance-formatted intermediate. An approved shot plan constrains both families.

Read [Project records](references/records.md) before creating or changing records. Start from [the brief template](assets/BRIEF.template.md); the [plan example](assets/plan.example.json) demonstrates the machine-readable fields. It is synthetic test data, not a creative proposal.

Resolve every bundled script path relative to this `SKILL.md`, then invoke it through Python with explicit project input/output paths. Keep the private project's working directory; do not write project data into the installed skill.

## From reference to proposal and images

Use [Story](references/story.md) to turn observed audience experience and user intent into alternative visual scripts. Review those scripts shot by shot before illustration, and derive the image count from the chosen music and readable actions.

By default, use the four stages in [Images](references/images.md), selecting one composition reference, making a two-image GPT blocking draft, completing it with Ideogram, then repairing localized details with GPT while preserving the established rendering and character appearance. When a reference-video frame already meets the shot requirements, direct frame editing may skip the blocking draft under the conditions in [Images](references/images.md). Save the ordered images actually submitted at every stage. Style comes from the user's chosen references.

## Review and execution boundaries

Confirm and record in `BRIEF.md` the user’s intent for appearance-affecting choices, including each input image’s composition, style, identity or wardrobe role, style source and clothing, before writing them into prompts. Do not turn unconfirmed assistant assumptions into requirements.

In collaborative work, present story plus storyboard before illustrations, one representative style test before the image batch, and the reviewed keyframes plus video cost before the video batch. These are reviewable artifacts, not repeated permission questions. Existing authorization covers the scope already approved. Autonomous review is allowed only within the user's recorded delegation; record the reasoning rather than inventing user approval.

No generation with unknown billing behavior or an unapproved provider substitution. Persist submission intent before a paid call. An ambiguous timeout is reconciled before resubmission. Price estimates are never reported as actual charges.

Validate the plan before execution with `python3 scripts/validate_plan.py PATH`. Local, unpaid helpers: `scripts/beat_grid.py` fits a beat grid to the target music (optional numpy/librosa); `scripts/render_edit.py` renders the plan's cut with speed, frame holds and dissolves. Use `python3 scripts/job_journal.py --help` for the local job record. Neither helper submits paid work. Record semantic and visual review separately from machine checks.

Completion requires inspecting the delivered artifact, verifying duration and audio, listing unresolved defects, and reconciling costs. A successful job status alone is insufficient.
