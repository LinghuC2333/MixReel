# Seedance 2 CG Video Prompt

Adapted from the user-authorized source IDE prompt rules. This file writes prompts only; it does not submit generation jobs. Verify the selected endpoint with [the provider contract](providers.md) before execution. Model IDs here identify source prompt families, not universal API identifiers.

Use this reference when the selected endpoint has been mapped to the Seedance 2 prompt family (source ID `video-seedance`). When the
active model is `video-minimax-h3`, use `prompt-minimax-h3.md` instead.
Do not run both prompt families for the same scene and do not use this output as an
intermediate step for H3.

This bundled authoring mode describes a single camera setup. Use it for a compatible single-shot generation group. A multi-shot group requires a separately verified endpoint format; do not silently split it into paid calls or assume this prompt alone enables multi-shot or video/audio conditioning.

Rewrite exactly one approved story beat into a concise, production-ready
Seedance 2 video direction. Preserve the named characters, background tags, props, story
meaning, spatial relationships, and intended emotional beat. Do not invent a
different event.

Organize the visible action around one major camera setup and state its behavior
explicitly. For a fixed camera, say no dolly, no zoom, and no pan. For a moving
camera, use at most one principal movement. Describe observable physical
reactions instead of abstract emotions, keep POV unambiguous, and give every
plot-critical prop its own sentence. Avoid readable on-screen text and never
fade to black. When exact outfit references already exist, do not repeat their
clothing details.

Do not add a style header, model, duration, ratio, resolution, reference labels,
reference lists, URLs, YAML, file paths, or executor commands. Sound must say
`无配乐，仅保留同期声`: synchronous dialogue, environmental sound, and action
sound are allowed; background music is not.

Return exactly one valid JSON object and no Markdown or commentary:

```json
{"description":"the finished video-specific description"}
```
