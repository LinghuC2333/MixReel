# From composition reference to finished keyframe

Use the user's selected style source, either their own artwork or frames from the reference video. If it is undecided, ask which source to use. Record the chosen images without prescribing a particular style.

Use these four stages by default for each keyframe; the direct-frame editing branch below may skip stage 1. Preserve the actual model/tool identity in the job record; a product label alone does not verify a model version. Resolve unavailable tools before submitting work, without silently replacing a stage.

Use the user-provided character consistency references as the authority for appearance. Their form is the user’s choice and may include headshots, full-body portraits, multi-angle sheets or expression sheets. Inspect what each covers and record it in `BRIEF.md`. Include the relevant references whenever editing that character; do not substitute intermediate artwork or crops from other works without user confirmation.

## 0. Select one composition reference

Write the shot's scale, subject count and image share, foreground/background relationship, and action that must remain visible. Use a suitable frame from the corresponding reference-video shot, or search Pinterest through an available OpenCLI installation.

Combine two or three short action, viewpoint or setting terms; keep story names and lore out of the query. Check the installed command's help before use. A search command may take this form.

```sh
opencli pinterest search-pins "<short terms>" --limit 10 -f json
```

Save search results, deduplicate candidates, download and open them. Compare framing, action and cropping visually, then search again for the missing condition if necessary. Tool access errors are not empty search results. Keep an unresolved shot incomplete when no candidate fits.

Select exactly one composition image per shot. Record its original URL, search terms or source-video time, borrowed composition and required changes. Show all selected images together to review repeated scale and angles. Candidate sheets are for selection, not extra generation inputs.

When a reference-video frame already meets the shot’s scale, staging and spatial requirements, it may serve directly as the first image for editing in stage 2, skipping the GPT draft. Edit people, clothing and scene details to match the approved shot. Assign its role from the style source recorded in `BRIEF.md`. It supplies composition and style only when the user chose reference-video style; otherwise it supplies composition only, with style supplied by the user’s selected style references. In the composition-only case, check the output for unwanted style influence from the base frame.

## 1. GPT creates a simple composition draft

Supply exactly two images, the selected composition reference and one simple-drawing example. Describe the scene, people count, framing, time of day, theme colors and simple clothing silhouettes in text.

Produce a colored blocking draft that preserves pose, relative size, depth and light/shadow. Leave character faces, hair and detailed clothing undeveloped. Do not include complete character portraits or a previous finished illustration at this stage. Review the draft against the shot requirements before continuing.

## 2. Ideogram applies the style and completes the people

Supply the draft or qualifying reference frame first, then the character consistency references and selected style images. Add a background reference only when needed. Use whole images, crops or a combined sheet according to what the references actually contain and their recorded roles. When several characters share an image, state their order within it separately from each character’s target-screen position and clothing; reference order does not determine scene placement.

Preserve composition, shot scale and time of day. Disable `magic_prompt` and retain the editing base’s dimensions, mapping those settings through the verified endpoint schema. Do not import another model's parameter names. Inspect the returned image against the editing base and the selected identity/style references.

Keep each character’s wardrobe consistent across a continuous scene, using the clothing choice confirmed by the user and recorded in `BRIEF.md`. If the character consistency reference includes that scene’s selected outfit, use it as the wardrobe reference. For a new outfit or references without clothing, once the first keyframe showing the outfit is approved, crop a wardrobe reference from it. Include that reference in subsequent edits involving the character and explicitly require matching clothing.

## 3. GPT corrects identity and visible details

Supply the Ideogram result and the relevant character consistency references, preserving their recorded identity, style and wardrobe roles. Use only the aspects assigned by the user; an identity reference does not authorize replacing the selected wardrobe.

Correct only observed deviations in visible features, hair, proportions or garment details. Keep the camera, action and subject size unchanged. Small or obscured faces remain small or obscured; assess only what is actually visible. Compare before and after, then review the complete set for consistency before video production.

Preserve regions outside the requested repair. If an edit changes them, a feathered mask may composite the corresponding regions from the pre-edit image back into the result. Compare before and after at enlarged scale to check seams and confirm that the remaining regions are unchanged.

## Record what was actually submitted

Before submission, state each input image’s role according to the user’s confirmed intent in `BRIEF.md`. For every generation or edit, save an ordered input-image manifest with stage, shot/job ID, file or stable asset ID, content hash, role and character mapping. Save the prompt, parameters and output IDs alongside it. Check the executor's actual inputs against this manifest, not just the planned bindings. Keep credentials and temporary signed links out of shareable records. Preserve originals and previous versions.
