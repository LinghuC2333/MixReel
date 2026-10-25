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

## Stage artifacts

Read [handoffs](handoffs.md) for independent stage entry and outputs. `reference-analysis.md`, `script.md`, `video-plan.md` and `keyframes.md` are default artifact names; preserve suitable existing project names. Link versions and review states from the brief. Borrowing dimensions and advertiser claim evidence belong in the brief/script, while actual submitted media roles belong in the asset inventory and job manifests. A script-only task does not need a complete production plan.

## Plan shape

The bundled example uses version 2 and is validated by `validate_plan.py`. Version 1 plans remain readable with their original per-shot keyframe requirements; migrate explicitly before using generation groups. Its durations and names are synthetic fixtures. The validator checks timeline and dependency consistency; it cannot judge taste or verify that a person is recognizable.

`duration` is the target timeline length. `music.duration` describes the source track; `music.offset` identifies the selected excerpt. Musical events are relative to that excerpt. Shots tile the timeline without gaps. `references` is a stable asset inventory. In version 2 every reference declares `media_type` as `image`, `video` or `audio`, alongside its user-assigned `role` and `contribution`. Roles also include `motion`, `timing` and `sound`; declaring a role does not establish endpoint support. Shot `bindings` identify the references that shot needs; group `bindings` give the ordered request inventory and must include all member-shot bindings. Save the actual submitted image inventory with each job as described in [Images](../../mixreel-keyframes/references/images.md); reconcile any difference before treating the stage as reviewed. Each shot has a visible scene, a keyframe design, source evidence, camera behavior and starting/ending state.

Version 2 requires a nonempty `generation_groups` list. Each entry has a unique `id`, ordered `shot_ids`, `requested_duration` in seconds, ordered reference `bindings`, a `reason` for the grouping or split, and `continuity` describing spatial/action states to preserve. `provider_prompt` is text or null while pending and belongs to the group, not a separate call for every shot. Groups must cover every shot exactly once, in timeline order, without interleaving. Requested duration must cover the group's planned timeline span; select a supported duration with necessary handles and verify limits and billing separately in the provider profile.

In version 2, a shot's `keyframe_design` still describes its visual intent, but `keyframes` may be empty or share image IDs with other shots. List only planned new illustration outputs there, each with a reason in the visual design; existing assets belong in `references`. `illustration_count` counts the unique new image IDs across shots, not references, intermediate image passes or paid image attempts. The group's image outputs are the union of its members' keyframe IDs. Save their stable assets/hashes with the actual submitted references before execution. Report `len(shots)`, `len(generation_groups)` and `illustration_count` separately. Keyframe review still records whether the selected visual inputs are sufficient even when no new image is needed.

The bundled synthetic plan demonstrates two editorial shots sharing one generation request with one new keyframe, plus video and audio reference roles. It does not claim those inputs are supported by any particular endpoint. Record capability evidence, estimated billable seconds, quotes and retry scope in the provider profile, brief and journal; requested seconds are not actual billed seconds.

`transition.duration` represents overlap leading into the incoming shot. It consumes extra source handles, not additional output duration. A rendered shot's `clip.in` includes the pre-transition handle; the clip must supply `(shot duration + incoming overlap) * speed` source seconds. `clip.duration` is the total duration of the source file, not the length of the selected excerpt. The validator checks that `clip.in + (shot duration + incoming overlap) * speed` does not exceed that total. The main shot event begins after that overlap. The generator may provide more footage; the editor chooses the usable interval.

After generation, member shots in a group use the same selected `clip.asset` and full source `clip.duration`, with independently observed `clip.in` and playback `speed`. Keep internal timing intact where it fits; adjust only from inspected footage. Several source excerpts can be rendered from that same file without separate generation jobs. Prompt-local shot times do not establish these source in-points.

`reviews` records creative checks. Values pending, approved and rejected describe the human review state. Automated test success cannot turn a pending review into approved. Costs and authority live in the journal and brief, not in a fabricated plan approval flag.

## Dependency invalidation

| Change | Recheck |
|---|---|
| Reference, audience or emotional goal | Candidate story, shot plan and all dependent media |
| Music excerpt or tempo interpretation | Timing, shot count, edits and only media that no longer fits |
| Character/style anchor | Affected images and clips, not unrelated analysis |
| A local image correction | That frame and generation groups using it, plus their dependent clips |
| Generation grouping or reference modality | Group prompt, capability checks, duration/cost estimate and affected source-to-edit mappings |
| In/out edit or export setting | Timeline/audio/export; do not regenerate images |
| Provider/model | Capability profile, affected prompts, cost and a representative quality test |

Existing jobs are queried before new ones are prepared. Retain rejected assets and the reasons so a resume cannot accidentally promote them. Stop at the requested deliverable, including proposal-only or image-only work.
