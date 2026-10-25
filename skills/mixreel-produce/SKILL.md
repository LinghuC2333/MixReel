---
name: mixreel-produce
description: Execute authorized video generation, recover existing jobs, edit accepted footage and export a short video with reconciled costs. Also handles local edit-only tasks from existing clips; requires verified provider capabilities before paid submission.
---

# Produce and edit video

## Entry and shared rules

Read the requested scope, accepted script and generation plan, actual reference assets, provider profile and existing journal. For edit-only work, accept existing footage and the edit requirements without forcing new generation. Read [handoffs](../mixreel/references/handoffs.md), [execution](../mixreel/references/execution.md), [providers](../mixreel/references/providers.md) and [production](references/production.md). Resolve credentials through [local configuration](../mixreel/references/local-config.md).

## Execute only the planned work

Before paid submission, verify plan and reference versions, real endpoint capabilities, prompt readiness and spending authority. One generation group is one submission intent. Reserve once, save submitting state before the call, then save the task ID. Query existing work on resume. An unknown timeout never authorizes another paid submit; a download failure retries retrieval only.

The package has no bundled paid client. Use the verified host tool/adapter and record actual model/provider/parameters. Do not report simulated or planned requests as submitted. With no paid authority, deliver the execution plan or perform only authorized local edits.

Inspect returned footage before choosing ranges using [video review](../mixreel-review/references/video-review.md). Preserve the reviewed internal sequence when it fits. Do not regenerate separate files for shots already present in a shared result.

## Edit and deliver

Use `<core>/scripts/render_edit.py` for supported local edits or a suitable host editor for other needs. This helper drops source-clip audio, adds a short music fade and can sharpen resized footage; it cannot fulfill dialogue/SFX/UI/caption requirements by itself. Verify the actual render preserves every approved layer. Do not declare an advertising video complete with required brand/UI/sound missing.

Return the requested master/preview with source ranges, edit settings, known limitations and actual/estimated/unknown costs clearly separated. Read [review](../mixreel-review/SKILL.md) to check the deliverable before completion. Delivery to external destinations requires the corresponding user authorization.
