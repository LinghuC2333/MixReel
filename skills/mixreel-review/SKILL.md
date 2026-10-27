---
name: mixreel-review
description: Inspect a script, keyframe, generated clip or finished video against approved intent and source evidence; locate defects, route minimal repairs and verify them. Use independently for existing artifacts without requiring new generation.
---

# Review and decide repairs

## Inputs and evidence

Accept the artifact to review, requested quality concerns, relevant approved specification and source/reference evidence. Read [handoffs](../mixreel/references/handoffs.md), [diagnosis](references/diagnosis.md) and [review criteria](references/review.md); use [video inspection](references/video-review.md) for footage.

For a production, review the assembled film the user will receive; generated footage is judged inside that cut, not as loose clips. Watch actual video and listen to audio when available. Report a sampled-frame review as sampled and silent inspection as silent. Never claim a camera move, seamless transition or audible event from one still. If approved targets are missing, separate observable defects from judgments that need that target.

## Find the narrowest useful repair

Tie each finding to artifact version and time/frame/region, the intended result, observed mismatch, impact and evidence confidence. Trace the earliest stage where the mismatch appears. Choose local edit, image repair, prompt correction, regeneration or script revision according to cause and affected dependencies. Keep accepted work elsewhere.

Route creative/script issues to script writing, image issues to keyframes, group/prompt issues to video planning, and generation/edit issues to production. This skill owns diagnosis and recheck, not a duplicate generation workflow. Use another skill only within authorized scope; a review-only request ends with recommendations. Keep the same journal for any authorized paid repair.

## Output

Write `review.md` with findings, repair destination, affected artifacts, proposed acceptance check and status. Distinguish pass, fail and not checked. A machine-valid file is not creatively approved. Reviewer judgments remain agent judgments unless the user has approved the version.

After an authorized repair, compare changed regions and full context against the same target and inspect unintended changes. Close findings only with new evidence. If evidence or generation access is unavailable, state the remaining test instead of declaring the result fixed.
