# Choose and preserve the visual treatment

## Style choice

Use the recorded choice of own-IP rendering or reference-video rendering. If neither is chosen, explain the concrete visual difference and ask once. A style lock records media, palette, line and brush behavior, lighting, material finish and forbidden drift based on the user's actual preferences. Do not infer that every project must be anime, impasto, monochrome or photorealistic.

Select a representative frame that tests the hardest relevant combination of face, material, space and scale. A close-up alone may not test a wide crowded scene. Use the smallest set that resolves the actual risk. Review this before producing the full batch.

## Reference roles

Maintain an ordered inventory giving each image's content hash, source, allowed contribution and unwanted carry-over.

| Role | Intended contribution | Typical contamination |
|---|---|---|
| Composition | Framing, pose, depth, placement | Palette, medium, lighting or source identities |
| Identity | Face, hair and distinguishing features | Portrait pose, background and clothing |
| Style | Rendering and material treatment | Source faces or environment |
| Wardrobe | Garment shape and detail | Full-body pose or physique |
| Environment | Place, architecture and spatial cues | Wrong season, daylight or camera position |
| Ending anchor | Desired final composition and state | A second starting scene or an unwanted cut |

Use stable, user-approved identity references. A new approved frame can become the identity anchor after comparing it to the intended character. A single image need not contain every person; different characters can have separate approved sources. Preserve original references rather than repeatedly cropping regenerated faces and accumulating drift.

## Select a route by evidence

A colored blocking sketch can control pose, geometry and palette before final rendering. Supply only the composition reference and a simple-sketch treatment when that is the requested first stage. Avoid detailed clothing or face references that make the sketch prematurely dictate the final look.

Test direct generation when the model already follows the target rendering. Test sketch-to-render when composition is difficult and the rendering model can reinterpret the sketch. Add a local identity or detail pass only where review identifies a defect. The model sequence is selected per treatment and current capabilities, not fixed by brand names.

If clothing references copy their pose into the image, try face crops plus explicit wardrobe description during composition/rendering, and apply garment detail in a controlled repair pass. If line-based artwork becomes flat, try direct generation with style references or a different rendering step. These are diagnosed remedies, not universal limitations of a named model.

## Review and repair

Inspect face resemblance, gaze, anatomy, pose, garment continuity, character count, scene time, palette and rendering. Compare at intended phone size as well as full resolution. Keep a contact sheet for consistency and full-resolution files for details.

For a spatially local edit, use a mask or equivalent region control when supported. Verify that provider's mask polarity and dimensions; black does not universally mean edit. Protect other people and unchanged areas. Compare before/after beyond the edited region.

A single rejected image does not justify regenerating the whole set. First retry only that image against the approved style and identity references. Expand the repair only if the shared style definition changed or comparisons show group-wide defects. Record superseded assets without overwriting originals.

Choose resolution for downstream output, crop margin and visible detail. Start near the target useful resolution; require a demonstrated benefit for expensive upscaling. Do not infer that a larger input guarantees a sharper video.

Approve the full keyframe set before the video batch. Count optional ending images separately. An ending reference in reference-only mode is a soft visual instruction, not a guaranteed endpoint constraint.
