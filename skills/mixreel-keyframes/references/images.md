# From composition source to finished keyframe

Use the user's selected style source, either their own artwork or frames from the reference video. If it is undecided, ask which source to use. Record the chosen images without prescribing a particular style.

Plan [generation groups](../../mixreel/references/motion-edit.md) first and create only the new keyframes needed to resolve visual uncertainty. Reuse accepted references or share a keyframe across shots when sufficient; keep textual visual designs for shots without a generated image. Each necessary new keyframe goes through two steps, generation and local editing. Preserve the actual model/tool identity in the job record; a product label alone does not verify a model version. Resolve unavailable tools before submitting work, without silently replacing a step.

Use the user-provided character consistency references as the authority for appearance. Their form is the user's choice and may include headshots, full-body portraits, multi-angle sheets or expression sheets. Inspect what each covers and record it in `BRIEF.md`. Include the relevant references whenever generating or editing that character; do not substitute intermediate artwork or crops from other works without user confirmation.

## Choose a model for each step by its strengths

Image models differ. One may carry a hand-drawn or painterly style across far better, while another follows detailed instructions far more exactly but cannot reach many styles. Use the style-strong model to generate and the instruction-following model to edit. By default, try Ideogram for generation and GPT for editing, then confirm the choice against this project's style on one representative image. Record which model did better on which task in the private project; a result on one style is not a general rule about the model.

## 0. Select the composition source

When a [spatial previs](../../mixreel-script/references/previs.md) exists, the shot's render is the composition source. It supplies layout only; its proxy colours and body shapes must not appear in the image.

Without a previs, write the shot's scale, subject count and image share, foreground/background relationship, and action that must remain visible. Use a suitable frame from the corresponding reference-video shot, or search Pinterest through an available OpenCLI installation.

Combine two or three short action, viewpoint or setting terms; keep story names and lore out of the query. Check the installed command's help before use. A search command may take this form.

```sh
opencli pinterest search-pins "<short terms>" --limit 10 -f json
```

Save search results, deduplicate candidates, download and open them. Compare framing, action and cropping visually, then search again for the missing condition if necessary. Tool access errors are not empty search results. Keep an unresolved shot incomplete when no candidate fits.

Select exactly one composition source for each new keyframe being produced. Record the previs shot, original URL, search terms or source-video time, borrowed composition and required changes. Show all selected images together to review repeated scale and angles. Candidate sheets are for selection, not extra generation inputs.

A reference-video frame supplies composition and style only when the user chose reference-video style; otherwise it supplies composition only, with style supplied by the user's selected style references. In the composition-only case, check the output for unwanted style influence from that frame.

## 1. Generate

Supply the composition source, the selected style images and the character consistency references, and state each image's role in the prompt. A style image that shows a person can pass that person's face, hair or figure to your characters. Prefer style references without faces, or crops limited to rendering and background; once an image from this project is approved, use it as the style reference for later frames. Add a background reference only when needed. Before a character's appearance and wardrobe are approved, keep earlier finished illustrations out so old clothing and details do not lock in. Use whole images, crops or a combined sheet according to what the references actually contain and their recorded roles. When several characters share an image, state their order within it separately from each character's target-screen position and clothing; reference order does not determine scene placement.

Check how the endpoint uses the composition source. Some treat a supplied image as an editing base and keep most of its pixels, others as a loose reference. Choose the mode that keeps the layout while replacing proxies or source people, and verify it on the first image. Preserve composition, shot scale and time of day. Turn off automatic prompt rewriting where the endpoint offers it and map size settings through the verified endpoint schema. Do not import another model's parameter names.

Keep each character's wardrobe consistent across a continuous scene, using the clothing choice confirmed by the user and recorded in `BRIEF.md`. If the character consistency reference includes that scene's selected outfit, use it as the wardrobe reference. For a new outfit or references without clothing, once the first keyframe showing the outfit is approved, crop a wardrobe reference from it. Include that reference in subsequent generations and edits involving the character and explicitly require matching clothing.

Judge the result by its style first.

- When the style is right and the rest is close, including a face that is nearly right, move to editing.
- When the style or the overall composition is wrong, generate again with revised inputs on the style-strong model. Generate with the instruction-following model only when it can reach this style, or when the user accepts the change in look.

## 2. Edit locally

Supply the generated image and the relevant character consistency references, preserving their recorded identity, style and wardrobe roles. Use only the aspects assigned by the user; an identity reference does not authorize replacing the selected wardrobe.

Name each defect and its region in the prompt, such as a face that drifts from its reference, a hand, a prop, a garment detail or a proportion, and require everything else to stay as it is. Face corrections move toward the character reference without redrawing the rendering. Keep the camera, action and subject size unchanged. Small or obscured faces remain small or obscured; assess only what is actually visible. If an edit changes the established rendering or the character's demeanor, reject it; edit again with a narrower instruction or return to generation.

For retries or further edits, follow [Diagnosis](../../mixreel-review/references/diagnosis.md) to choose the original inputs or a different step or model. Preserve regions outside the requested edit. If an edit changes them, a feathered mask may composite the corresponding regions from the pre-edit image back into the result. Compare before and after at enlarged scale to check seams and confirm that the remaining regions are unchanged. Review the complete set for consistency before video production.

## Confirm that each pass did its job

A finished job and a charge do not prove that a generation or edit changed anything. After every pass, compare the output with its input image at full size and measure the pixel difference. An output identical or nearly identical to that input means the pass had no effect on this endpoint, even when it was billed. Record it as ineffective and stop that route; do not resubmit the same request.

Run a new model or changed step on one representative image before applying it across a batch. When a model proves ineffective for a step, report the evidence and propose an alternative model or route. The user decides; never switch silently.

## Record what was actually submitted

Before submission, state each input image's role according to the user's confirmed intent in `BRIEF.md`. For every generation or edit, save an ordered input-image manifest with step, shot/job ID, file or stable asset ID, content hash, role and character mapping. Save the prompt, parameters and output IDs alongside it. Check the executor's actual inputs against this manifest, not just the planned bindings. Keep credentials and temporary signed links out of shareable records. Preserve originals and previous versions.
