# Read the reference and music

## Reference evidence

Inspect the actual video, not just its thumbnail or extracted middle frames. Obtain a local copy through an available authorized tool, retaining source URL and provenance in private project records. If access fails, report which observations are missing; do not invent camera motion from a still.

Use `python3 <core>/scripts/media_inspect.py reference VIDEO OUTPUT_DIR` for cut candidates and time-labelled stills. Automated cuts can miss dissolves and slow reveals. Watch each candidate shot and its boundaries. A sequence of stills helps, but cannot prove smoothness or motion direction.

Write one row per shot containing source time range, subject placement and size, viewing angle, gaze target, camera start/movement/end, subject movement, occlusion, light, transition, emotional function and evidence confidence. Separate observed movement from inferred technique. A widening view may be subject motion rather than a camera pullback.

Then state what makes the viewer anticipate the next image. Identify the opening question, the change in information, peak feeling and what the ending withholds or resolves. Treat performance data as user-supplied or verified evidence; aesthetic analysis cannot prove a video's commercial success.

Classify movement per shot as primarily camera, primarily performance or mixed. This is a production choice, not a demand for uniformly static or uniformly dramatic footage.

## Target music

The target track controls the new timeline. Keep source offsets when using an excerpt. Honor an already selected excerpt; if only a full track is supplied, propose a compact phrase-complete excerpt within the requested duration.

`python3 <core>/scripts/media_inspect.py audio AUDIO OUTPUT.json` reports duration, silence and candidate onsets. Optional beat tracking: `python3 <core>/scripts/beat_grid.py AUDIO OUTPUT.json --bpm HINT` fits a regular grid and reports kick/hat strength per beat (requires numpy and librosa). Record method, confidence, drum entry, phrase changes, strong accents and ending. Listen around those events. The kick/hat fields are frequency-band energy estimates, not verified instrument labels. `bar_start` groups the fitted grid using `--bar` (default 4); it does not detect downbeats. A regular fitted grid does not establish where the musical phrase begins. Do not assume every song is four-four, every phrase has eight beats, or every detected transient needs a cut.

Sketch the available visual slots using music events and the time each action needs. Report timeline shots, generation requests and unique new illustrations separately; decide the latter two after [grouping the sequence](../../mixreel/references/motion-edit.md). Do not equate one beat with one image.

## Dimensions and handoff

Record content/composition, script/information, hook, music/sound, edit rhythm/motion and style/presentation independently, with source times and uncertainty. Quote or transcribe relevant copy when actually available. Explain which event changes what the viewer expects. Record audience knowledge or lyrical/sound dependencies; do not substitute generic labels such as viral or cinematic for observations.

The user's intent determines which dimensions to borrow. Suggest options with reasons; the script stage records selected treatments using [adaptation decisions](../../mixreel-script/references/adaptation.md). Target audio may require new timing without replacing the selected creative mechanism. Missing audio leaves that part pending.

Stop at analysis when requested. Script writing maps selected functions to new content and timing; keyframe production searches for missing composition evidence only after a concrete need is established. Do not search Pinterest or generate extra images merely to complete an analysis report.
