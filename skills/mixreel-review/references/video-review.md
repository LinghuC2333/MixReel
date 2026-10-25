# Inspect generated video


Watch each returned sequence through its internal cuts before selecting footage. Check that positions, screen direction, contacts and action speed remain continuous and the planned events are present. Compare observed cuts and accents with the request-local plan; prompt timestamps are not proof of frame-accurate timing. Watch the actual returned clips, including beginning and end. Check subject identity, rendering, contact, direction, gaze, final state and camera movement. Inspect gaze throughout each clip against the approved targets, especially during turns, looks back and camera moves that reveal a face. If a character unexpectedly looks into the lens, first try adjusting the in-point and playback speed to exclude that interval while preserving the required action and timing; regenerate only if editing cannot avoid it. A finished provider job can still be unusable.

Use `python3 <core>/scripts/media_inspect.py motion CLIP OUTPUT.json` to locate candidate visual changes. Frame-difference peaks can be a camera move, flash or defect. Inspect surrounding frames to identify the intended narrative accent. Record actual event time and confidence; prompt timestamps are not observations.

