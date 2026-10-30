# Block the space before images

A video model must keep positions, facings and the camera consistent from shot to shot. A text table hides a figure blocking the subject or a cut flipping screen direction until paid generation shows it; a spatial previs finds them first, at no cost.

## When to build one

Build it for the shots the script marks as video. Skip it only when existing reference frames already prove the layout of every video shot, and record why. Image shots need none, since each image's composition is settled when its keyframe is made, and post shots are composited in the edit.

## Render it

Write the scene once as a scene file and render it with `scripts/previs.py`; `--schema` prints the format and [the example scene](../assets/previs-scene.example.json) is a complete one. Blender renders it when installed, found on the PATH or in the usual install folders, such as `/Applications/Blender.app` on macOS. Let the script look rather than `which blender`, which misses app installs; when Blender is missing the script stops. Ask the user to install Blender, free from blender.org. If they would rather not, ask to download its `bpy` package, several hundred MB, and rerun with `--backend bpy` for the same images. If they decline that too, or there is no network, use `--backend raster`, which needs only numpy and Pillow. It shows positions, occlusion, screen direction and framing without shadows or depth of field; call its renders rough whenever you show or use them. A missing Blender is never a reason to skip the previs.

## Build the blocking scene

Real scale matters more than detail.

- Each named character is a proxy in its own flat colour; keep the colour legend fixed for the project. Plot-critical props and architecture get real positions, such as a throne, a pedestal, a doorway or a staircase.
- Actors move by keys on the film's one timeline, so the end of one shot and the start of the next come from the same scene. Each video shot gets a camera with start and end positions, look targets and vertical field of view; the frame size follows the delivery aspect ratio.
- Keep the scene file beside the renders as the record of positions, facings, gaze targets, held props and cameras.

Proxies do not prove faces, gaze nuance, hand contact or performance. Record those as not checked.

## Review outputs

Render the plan and the few shots most at risk first with `--shots`, and show them before building the rest. Extend to every video shot after the user accepts the direction.

- `plan.png` is drawn straight down, with names, movement arrows and each camera's position and facing.
- Each shot gets a start and an end frame, and `review.png` lays them out with shot IDs. Check that the subject is not hidden behind foreground figures, that screen direction and eyelines hold across cuts, what lies behind each subject, where every plot prop is, and whether each action fits its time.
- Fix problems inside the scene file, for example by moving a camera or opening a gap in a formation, then render again.
- With Blender, `--save-blend` also saves `previs.blend`, the whole film on one timeline with a marker at each cut that switches to that shot's camera. The user can scrub it in Blender, and `blender -b previs.blend -a` renders it as a moving preview.

## Use the results downstream

- A shot render can be the composition source for a keyframe, in place of a searched or reference-video frame.
- `storyboard.png` lays the rendered shots out in playback order with only a panel number on each. Keep captions, UI and production notes out of any sheet given to a model.
- When the video endpoint accepts it, the storyboard sheet can be the first ordered reference image. The prompt then states the colour legend and that mannequins, numbers, colours and grid lines must not be drawn.
- Previs renders supply layout only. Never use them as style or identity references.
