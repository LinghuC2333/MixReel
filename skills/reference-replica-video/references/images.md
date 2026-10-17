# From composition reference to finished keyframe

Use the user's selected style source, either their own artwork or frames from the reference video. If it is undecided, ask which source to use. Record the chosen images without prescribing a particular style.

Follow these four stages for each keyframe. Preserve the actual model/tool identity in the job record; a product label alone does not verify a model version. Resolve unavailable tools before submitting work, without silently replacing a stage.

## 0. Select one composition reference

Write the shot's scale, subject count and image share, foreground/background relationship, and action that must remain visible. Use a suitable frame from the corresponding reference-video shot, or search Pinterest through an available OpenCLI installation.

Combine two or three short action, viewpoint or setting terms; keep story names and lore out of the query. Check the installed command's help before use. A search command may take this form.

```sh
opencli pinterest search-pins "<short terms>" --limit 10 -f json
```

Save search results, deduplicate candidates, download and open them. Compare framing, action and cropping visually, then search again for the missing condition if necessary. Tool access errors are not empty search results. Keep an unresolved shot incomplete when no candidate fits.

Select exactly one composition image per shot. Record its original URL, search terms or source-video time, borrowed composition and required changes. Show all selected images together to review repeated scale and angles. Candidate sheets are for selection, not extra generation inputs.

## 1. GPT creates a simple composition draft

Supply exactly two images, the selected composition reference and one simple-drawing example. Describe the scene, people count, framing, time of day, theme colors and simple clothing silhouettes in text.

Produce a colored blocking draft that preserves pose, relative size, depth and light/shadow. Leave character faces, hair and detailed clothing undeveloped. Do not include complete character portraits or a previous finished illustration at this stage. Review the draft against the shot requirements before continuing.

## 2. Ideogram applies the style and completes the people

Supply the draft first, then the original face-reference collage, then the selected style images. Add a background reference only when needed. State the collage's left-to-right identity order, and separately state each character's target-screen position and clothing. Explain each input's role; collage order does not determine scene placement.

Preserve composition, shot scale and time of day. Disable `magic_prompt` and retain the draft's dimensions, mapping those settings through the verified endpoint schema. Do not import another model's parameter names. Inspect the returned image against the draft and the selected identity/style references.

## 3. GPT corrects identity and visible details

Supply the Ideogram result and the relevant character references. When retaining original clothing, use the character portraits. For changed clothing, use original face references and style images, keeping the newly selected wardrobe.

Correct only observed deviations in visible features, hair, proportions or garment details. Keep the camera, action and subject size unchanged. Small or obscured faces remain small or obscured; assess only what is actually visible. Compare before and after, then review the complete set for consistency before video production.

## Record what was actually submitted

For every generation or edit, save an ordered input-image manifest with stage, shot/job ID, file or stable asset ID, content hash, role and character mapping. Save the prompt, parameters and output IDs alongside it. Check the executor's actual inputs against this manifest, not just the planned bindings. Keep credentials and temporary signed links out of shareable records. Preserve originals and previous versions.
