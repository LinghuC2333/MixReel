---
name: mixreel-analyze
description: Analyze reference video and target audio for time-labelled visual, hook, script, music, editing and style evidence. Use independently before adaptation; does not write a finished script or generate media.
---

# Analyze a reference

## Inputs and entry

Accept a reference video or authorized accessible URL, the user's question or proposed borrowing scope, and target audio when supplied. Read the existing brief and [handoffs](../mixreel/references/handoffs.md). Existing time-labelled analysis can be reused after checking its source/version and coverage. Missing target audio does not prevent visual analysis.

Read [analysis](references/analysis.md). Watch the source through its cuts; sampled frames alone do not establish movement or timing. If the host cannot watch or hear it, identify exactly which observations are unavailable and label the result partial. Do not claim to have watched embedded videos from document text.

## Deliver

Write `reference-analysis.md` with source identity, time-labelled observations, the viewer's changing information, observed sound/text, and evidence confidence. Record content/composition, script progression, hook, music, edit rhythm, camera/performance and style separately. Suggest useful dimensions without treating suggestions as the user's choices. Preserve intentional links such as a lyric reveal or sound-based joke.

For supplied target audio, include excerpt offsets, musical phrase/accents, uncertainty and listening checks. Keep creative mechanics separate from the new edit timing. Do not treat views as proof of conversion or an identified cause of success.

Use `<core>/scripts/media_inspect.py` and optional `beat_grid.py` for candidates, then inspect the actual media. These tools do not replace viewing or listening. Update only source/evidence records; hand off to script writing when requested, without silently proceeding to production.
