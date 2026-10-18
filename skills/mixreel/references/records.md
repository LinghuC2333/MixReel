# Project records and continuation

## Files and authority

Keep the private project outside the installed skill. Use these records without duplicating the same decision in several places.

| File | Owner of the information |
|---|---|
| `BRIEF.md` | User intent, source provenance, creative choices, review decisions, next action |
| `plan.json` | Timed shots, reference roles, keyframe identifiers, source ranges and transitions |
| `providers/` | Verified service capabilities and project-specific parameter mappings |
| `journal.json` | Paid job lifecycle, reservations and billing evidence |
| `media/` | Immutable generated or downloaded artifacts, addressed by version/hash |
| `review.md` | Visual/semantic findings tied to artifact versions and delivery checks |

The brief links to other records. The latest user instruction overrides an older brief; reconcile and update it rather than silently following stale approval. Write which artifact version an approval covers, who approved it, the scope and evidence pointer. Agent review is labelled agent review, never user approval.

## Plan shape

The bundled example is validated by `validate_plan.py`. Its durations and names are synthetic fixtures. The validator checks timeline and dependency consistency; it cannot judge taste or verify that a person is recognizable.

`duration` is the target timeline length. `music.duration` describes the source track; `music.offset` identifies the selected excerpt. Musical events are relative to that excerpt. Shots tile the timeline without gaps. `references` is a stable asset inventory; `bindings` gives the planned ordered IDs for each provider request. Save the actual submitted image inventory with each job as described in [Images](images.md); reconcile any difference before treating the stage as reviewed. Each shot has a visible scene, a keyframe design, source evidence, camera behavior and starting/ending state.

`transition.duration` represents overlap leading into the incoming shot. It consumes extra source handles, not additional output duration. A rendered shot's `clip.in` includes the pre-transition handle; the clip must supply `(shot duration + incoming overlap) * speed` source seconds. `clip.duration` is the total duration of the source file, not the length of the selected excerpt. The validator checks that `clip.in + (shot duration + incoming overlap) * speed` does not exceed that total. The main shot event begins after that overlap. The generator may provide more footage; the editor chooses the usable interval.

`reviews` records creative checks. Values pending, approved and rejected describe the human review state. Automated test success cannot turn a pending review into approved. Costs and authority live in the journal and brief, not in a fabricated plan approval flag.

## Dependency invalidation

| Change | Recheck |
|---|---|
| Reference, audience or emotional goal | Candidate story, shot plan and all dependent media |
| Music excerpt or tempo interpretation | Timing, shot count, edits and only media that no longer fits |
| Character/style anchor | Affected images and clips, not unrelated analysis |
| A local image correction | That frame and clips derived from it |
| In/out edit or export setting | Timeline/audio/export; do not regenerate images |
| Provider/model | Capability profile, affected prompts, cost and a representative quality test |

Existing jobs are queried before new ones are prepared. Retain rejected assets and the reasons so a resume cannot accidentally promote them. Stop at the requested deliverable, including proposal-only or image-only work.
