# Read the reference and music

## Reference evidence

Inspect the actual video, not just its thumbnail or extracted middle frames. Obtain a local copy through an available authorized tool, retaining source URL and provenance in private project records. If access fails, report which observations are missing; do not invent camera motion from a still.

Use `python3 scripts/media_inspect.py reference VIDEO OUTPUT_DIR` for cut candidates and time-labelled stills. Automated cuts can miss dissolves and slow reveals. Watch each candidate shot and its boundaries. A sequence of stills helps, but cannot prove smoothness or motion direction.

Write one row per shot containing source time range, subject placement and size, viewing angle, gaze target, camera start/movement/end, subject movement, occlusion, light, transition, emotional function and evidence confidence. Separate observed movement from inferred technique. A widening view may be subject motion rather than a camera pullback.

Then state what makes the viewer anticipate the next image. Identify the opening question, the change in information, peak feeling and what the ending withholds or resolves. Treat performance data as user-supplied or verified evidence; aesthetic analysis cannot prove a video's commercial success.

Classify movement per shot as primarily camera, primarily performance or mixed. This is a production choice, not a demand for uniformly static or uniformly dramatic footage.

## Target music

The target track controls the new timeline. Keep source offsets when using an excerpt. Honor an already selected excerpt; if only a full track is supplied, propose a compact phrase-complete excerpt within the requested duration.

`python3 scripts/media_inspect.py audio AUDIO OUTPUT.json` reports duration, silence and candidate onsets. Optional beat tracking can use a locally available audio-analysis tool. Record method, confidence, drum entry, phrase changes, strong accents and ending. Listen around those events. A regular fitted grid does not establish where the musical phrase begins. Do not assume every song is four-four, every phrase has eight beats, or every detected transient needs a cut.

Sketch the available visual slots using music events and the time each action needs. Report timeline shots, starting illustrations, optional ending illustrations and total unique illustrations separately. Do not equate one beat with one image.

## Transfer and fill gaps

Map each reference shot's function to a slot on the target music. Keep emotional progression while allowing removal, merging, extension or an additional shot when duration changes. State what each change contributes. Do not retain a weak shot only to preserve numbering.

For each planned shot, select one composition reference using [Images, stage 0](images.md). A usable reference-video frame can supply it directly; otherwise define the missing visual requirements before searching Pinterest. Deliver the selected images and their source/adjustment notes together.
