# The Last Princess · First Meeting, production notes

A record of how the showcase short was made with this skill, including what went wrong. Project files, keys and paid-service records stay in the private project folder; only the published media is in this directory.

## Inputs

- Reference video, 19 seconds, hand-drawn greyscale ballroom meet-cute in four shots.
- Music, a 16.552-second excerpt of "Own The Dark", 145 BPM, drum entry at 4.164 s, heaviest kick at 10.785 s, closing hits at 14.509 s and 14.923 s.
- Story, chapters 19, 20 and 23 of the romance novel *The Last Princess* (rebels storm the palace, the rebel and the princess meet, the slap and the mark it leaves).
- Character references, the official character art for Elvina and Aiden.
- Style source, chosen by the user, the look of the reference video in pure greyscale.

## Script

The agent mapped each reference shot's job to the new music and story. The reference has four shots; the new cut has six because the slap and its aftermath needed their own beats.

| Shot | Time (s) | Music | What the viewer sees |
|---|---|---|---|
| 1 | 0.000–4.164 | intro | From behind, the princess at the top of the stairs while the palace is stormed |
| 2 | 4.164–7.475 | drum entry | Among the rebels, his gaze stops on someone up the stairs |
| 3 | 7.475–10.785 | third phrase | Past his shoulder, she looks back at him through the fleeing crowd |
| 4 | 10.785–14.095 | heaviest kick | He grabs her wrist; the camera tilts up to her glare |
| 5 | 14.095–14.923 | closing hit 1 | She slaps him and tears free |
| 6 | 14.923–16.552 | closing hit 2 | He lowers his hand, shows the handprint, a faint smile |

## Keyframes

Eight keyframes, one per shot plus the end frames of shots 4 and 6.

- Shots 1, 2, 3 and the end of shot 4 started from reference-video frames used directly as edit bases in Ideogram 4.5, because the user wanted the reference's rendering. Each edit received the base frame, the official character art and a few more reference frames for rendering.
- Shot 5 started from a full reference frame with the princess on the right; the edit added the rebel on the empty left side.
- Shot 6 started from a crop of the approved shot 2 keyframe, so his face and jacket match.
- Shot 4's opening (the grab) and shot 5 needed hand repairs. GPT Image 2.5 fixed the hands; where it also changed a face, the original face region was composited back with a feathered mask.
- Each character got one wardrobe reference cropped from an approved frame, passed into every later edit.

## Video and edit

- MiniMax H3 in reference mode, 768P, 9:16, one clip per shot, 4 or 5 seconds each. Inputs per clip were the keyframe(s), the character face in greyscale and one reference frame for rendering.
- The agent watched every clip, used frame-difference analysis to find the real slap (1.72 s into its clip) and placed it on the 14.509 s hit.
- Clips were retimed between 1.0× and 1.6× and rendered with twelve drawings per second at 24 fps.

## Cost

Quotes and estimates from the services, not reconciled bills.

| | Kept in the final cut | Including all tests |
|---|---|---|
| Images | about $2.10 (9 Ideogram edits, 2 GPT repairs) | about $7.30 |
| Video | ¥13.0 (26 s at 768P) | ¥16.2 (with one 2K comparison clip) |

## Known defects

- For about a third of a second in shot 4 and at the end of shot 5, the princess glances into the lens.
- Shot 1 keeps the reference's framing, so she is larger in the frame than the script asked for.

## What this production changed in the skill

The first passes followed the default four-stage image workflow and came out flat compared with the reference. The review produced several general rules that were merged into the skill.

- Confirm image roles and the style source with the user before writing prompts.
- Let a reference frame that already fits the shot serve as the edit base.
- Treat whatever character reference the user supplies as the identity authority.
- Keep wardrobe consistent with a reference image across a scene.
- Protect regions outside a local repair.
- Never feed a model its own previous output as the base for the next version.
- Check returned clips for unexpected glances into the lens.
