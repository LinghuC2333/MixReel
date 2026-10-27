#!/usr/bin/env python3
"""Validate a reference-led video's timeline and bindings. No network or writes."""
import argparse
import json
import math
from pathlib import Path


def validate(plan):
    errors = []
    def fail(path, message):
        errors.append(f'{path}: {message}')
    def number(value, path, positive=False):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            fail(path, 'expected a finite number')
            return None
        if value < 0 or (positive and value == 0):
            fail(path, 'expected a positive number' if positive else 'expected a nonnegative number')
            return None
        return value
    def text(obj, key, path):
        if not isinstance(obj.get(key), str) or not obj[key].strip():
            fail(f'{path}.{key}', 'nonempty text required')
    if not isinstance(plan, dict):
        return ['plan: expected an object']
    version = plan.get('version')
    if isinstance(version, bool) or version not in (1, 2, 3):
        fail('version', 'unsupported or missing version')
    if version == 1 and 'generation_groups' in plan:
        fail('generation_groups', 'use version 2 for grouped generation')
    if version in (1, 2):
        for key in ('overlays', 'sound'):
            if key in plan: fail(key, 'use version 3 for overlays and mixed sound')
    duration = number(plan.get('duration'), 'duration', True)
    fps = number(plan.get('fps'), 'fps', True)
    tolerance = 0.5 / fps if fps else 0.001
    music = plan.get('music', {})
    if not isinstance(music, dict):
        music = {}; fail('music', 'expected an object')
    # Version 3 can take its score from generated clip audio or have none at all.
    music_source = music.get('source', 'track') if version == 3 else 'track'
    if music_source not in ('track', 'generated', 'none'):
        fail('music.source', 'expected track, generated or none')
    if music_source == 'track':
        text(music, 'asset', 'music')
        source_duration = number(music.get('duration'), 'music.duration', True)
        offset = number(music.get('offset'), 'music.offset')
        if None not in (source_duration, offset, duration) and offset + duration > source_duration + tolerance:
            fail('music', 'selected excerpt exceeds source duration')
    events = music.get('events', [])
    if not isinstance(events, list):
        events = []; fail('music.events', 'expected a list')
    event_ids = set()
    for i, event in enumerate(events):
        p = f'music.events[{i}]'
        if not isinstance(event, dict):
            fail(p, 'expected an object'); continue
        text(event, 'id', p); text(event, 'kind', p)
        eid = event.get('id')
        if isinstance(eid, str):
            if eid in event_ids: fail(p, 'duplicate event id')
            event_ids.add(eid)
        at = number(event.get('time'), p + '.time')
        if duration is not None and at is not None and at > duration:
            fail(p, 'event outside excerpt')
    refs = plan.get('references', [])
    if not isinstance(refs, list):
        refs = []; fail('references', 'expected a list')
    ref_ids = set()
    allowed_roles = {'composition', 'identity', 'style', 'wardrobe', 'environment', 'ending_anchor'}
    if version in (2, 3):
        allowed_roles.update(('motion', 'timing', 'sound'))
    for i, ref in enumerate(refs):
        p = f'references[{i}]'
        if not isinstance(ref, dict):
            fail(p, 'expected an object'); continue
        for k in ('id', 'asset', 'role', 'contribution'): text(ref, k, p)
        rid = ref.get('id')
        if isinstance(rid, str):
            if rid in ref_ids: fail(p, 'duplicate reference id')
            ref_ids.add(rid)
        if not isinstance(ref.get('role'), str) or ref['role'] not in allowed_roles:
            fail(p, 'unknown reference role')
        if version in (2, 3) and ref.get('media_type') not in ('image', 'video', 'audio'):
            fail(p + '.media_type', 'expected image, video or audio')
    reviews = plan.get('reviews', {})
    if not isinstance(reviews, dict):
        fail('reviews', 'expected an object')
    else:
        for key in ('storyboard', 'style', 'keyframes'):
            if reviews.get(key) not in ('pending', 'approved', 'rejected'):
                fail('reviews.' + key, 'expected pending, approved or rejected')
    shots = plan.get('shots')
    if not isinstance(shots, list) or not shots:
        fail('shots', 'nonempty list required'); return errors
    previous_end = 0.0
    previous_length = 0.0
    shot_ids, frame_ids = set(), set()
    for i, shot in enumerate(shots):
        p = f'shots[{i}]'
        if not isinstance(shot, dict):
            fail(p, 'expected an object'); continue
        for k in ('id', 'function', 'source_evidence', 'keyframe_design', 'description', 'opening', 'ending'):
            text(shot, k, p)
        sid = shot.get('id')
        if isinstance(sid, str):
            if sid in shot_ids: fail(p, 'duplicate shot id')
            shot_ids.add(sid)
        start = number(shot.get('start'), p + '.start')
        end = number(shot.get('end'), p + '.end')
        if start is not None and abs(start - previous_end) > tolerance:
            fail(p, 'timeline gap or overlap')
        length = end - start if None not in (start, end) else None
        if length is not None and length <= 0: fail(p, 'end must follow start')
        camera = shot.get('camera')
        if not isinstance(camera, dict): fail(p + '.camera', 'expected an object')
        else:
            for k in ('behavior', 'start', 'end'): text(camera, k, p + '.camera')
        bindings = shot.get('bindings')
        if not isinstance(bindings, list) or any(not isinstance(b, str) for b in bindings):
            fail(p + '.bindings', 'expected an ordered list of reference IDs')
        else:
            if len(set(bindings)) != len(bindings): fail(p + '.bindings', 'duplicate binding')
            for b in bindings:
                if b not in ref_ids: fail(p + '.bindings', 'unknown reference ' + b)
        kfs = shot.get('keyframes')
        if not isinstance(kfs, list) or (version == 1 and not kfs) or any(not isinstance(k, str) or not k.strip() for k in kfs):
            fail(p + '.keyframes', 'nonempty list of image IDs required' if version == 1
                 else 'list of image IDs required (may be empty from version 2)')
        else: frame_ids.update(kfs)
        event = shot.get('music_event')
        if event is not None and (not isinstance(event, str) or event not in event_ids):
            fail(p + '.music_event', 'unknown music event')
        transition = shot.get('transition', {'type': 'cut', 'duration': 0})
        pad = 0.0
        if not isinstance(transition, dict): fail(p + '.transition', 'expected an object')
        else:
            if transition.get('type') not in ('cut', 'dissolve'): fail(p + '.transition', 'unsupported transition')
            t = number(transition.get('duration'), p + '.transition.duration')
            if t is not None:
                pad = t
                if transition.get('type') == 'cut' and t != 0: fail(p + '.transition', 'cut overlap must be zero')
                if transition.get('type') == 'dissolve' and t == 0: fail(p + '.transition', 'dissolve requires overlap')
                if i == 0 and t: fail(p + '.transition', 'first shot cannot overlap a predecessor')
                if i and (t > previous_length or (length is not None and t > length)):
                    fail(p + '.transition', 'overlap exceeds adjacent shot length')
        clip = shot.get('clip')
        if clip is not None:
            if not isinstance(clip, dict): fail(p + '.clip', 'expected an object')
            else:
                text(clip, 'asset', p + '.clip')
                cin = number(clip.get('in'), p + '.clip.in')
                cd = number(clip.get('duration'), p + '.clip.duration', True)
                speed = number(clip.get('speed'), p + '.clip.speed', True)
                if None not in (cin, cd, speed, length) and cin + (length + pad) * speed > cd + tolerance:
                    fail(p + '.clip', 'source clip lacks requested range or transition handle; '
                         f'required source end {cin + (length + pad) * speed:g}s exceeds '
                         f'clip.duration {cd:g}s (total source-file duration)')
                if 'repair' in clip:
                    if version != 3: fail(p + '.clip.repair', 'use version 3 for repair clips')
                    else: text(clip, 'repair', p + '.clip')
        if version == 3:
            validate_shot_v3(shot, p, length, pad, fps, tolerance, fail, number, text)
        if end is not None: previous_end = end
        if length is not None: previous_length = length
    if duration is not None and abs(previous_end - duration) > tolerance:
        fail('shots', 'timeline does not end at target duration')
    count = plan.get('illustration_count')
    if isinstance(count, bool) or not isinstance(count, int) or count != len(frame_ids):
        fail('illustration_count', f'expected {len(frame_ids)} unique images')
    if version in (2, 3):
        validate_groups(plan.get('generation_groups'), shots, ref_ids, tolerance, fail, number, text, version)
    if version == 3:
        validate_layers(plan, duration, fps, tolerance, fail, number, text)
    return errors


def validate_shot_v3(shot, p, length, pad, fps, tolerance, fail, number, text):
    """Per-shot frame holds and the source of each shot's sound."""
    if 'holds' in shot:
        holds = number(shot['holds'], p + '.holds', True)
        if holds is not None and fps and holds > fps:
            fail(p + '.holds', 'cannot exceed fps')
    audio = shot.get('audio', {'from': 'clip'})
    if not isinstance(audio, dict):
        fail(p + '.audio', 'expected an object'); return
    source = audio.get('from')
    if source not in ('clip', 'asset', 'none'):
        fail(p + '.audio.from', 'expected clip, asset or none')
    elif source == 'asset':
        # A picture-only replacement keeps another file's sound, usually the original generated clip.
        text(audio, 'asset', p + '.audio')
        ain = number(audio.get('in'), p + '.audio.in')
        ad = number(audio.get('duration'), p + '.audio.duration', True)
        speed = number(audio.get('speed', 1), p + '.audio.speed', True)
        if None not in (ain, ad, speed, length) and ain + (length + pad) * speed > ad + tolerance:
            fail(p + '.audio', 'audio source lacks requested range')


def validate_layers(plan, duration, fps, tolerance, fail, number, text):
    """Edit-layer overlays and extra sound placed on the final timeline."""
    overlays = plan.get('overlays', [])
    if not isinstance(overlays, list):
        fail('overlays', 'expected a list'); overlays = []
    ids = set()
    for i, overlay in enumerate(overlays):
        p = f'overlays[{i}]'
        if not isinstance(overlay, dict):
            fail(p, 'expected an object'); continue
        text(overlay, 'id', p); text(overlay, 'asset', p)
        if overlay.get('id') in ids: fail(p, 'duplicate overlay id')
        ids.add(overlay.get('id'))
        start = number(overlay.get('start'), p + '.start')
        end = number(overlay.get('end'), p + '.end')
        if None not in (start, end) and end <= start: fail(p, 'end must follow start')
        if None not in (end, duration) and end > duration + tolerance: fail(p, 'overlay outside timeline')
        if 'fps' in overlay: number(overlay['fps'], p + '.fps', True)
        if isinstance(overlay.get('asset'), str) and '%' in overlay['asset'] and 'fps' not in overlay:
            fail(p + '.fps', 'image sequence needs fps')
    sound = plan.get('sound', {})
    if not isinstance(sound, dict):
        fail('sound', 'expected an object'); return
    for i, duck in enumerate(sound.get('ducking', []) if isinstance(sound.get('ducking', []), list) else []):
        p = f'sound.ducking[{i}]'
        if not isinstance(duck, dict): fail(p, 'expected an object'); continue
        start = number(duck.get('start'), p + '.start'); end = number(duck.get('end'), p + '.end')
        gain = number(duck.get('gain'), p + '.gain')
        if None not in (start, end) and end <= start: fail(p, 'end must follow start')
        if None not in (end, duration) and end > duration + tolerance: fail(p, 'ducking outside timeline')
        if gain is not None and gain > 1: fail(p + '.gain', 'ducking gain must be at most 1')
    if not isinstance(sound.get('ducking', []), list): fail('sound.ducking', 'expected a list')
    layers = sound.get('layers', [])
    if not isinstance(layers, list):
        fail('sound.layers', 'expected a list'); layers = []
    for i, layer in enumerate(layers):
        p = f'sound.layers[{i}]'
        if not isinstance(layer, dict): fail(p, 'expected an object'); continue
        text(layer, 'id', p); text(layer, 'asset', p)
        at = number(layer.get('at'), p + '.at')
        if 'gain' in layer: number(layer['gain'], p + '.gain')
        if None not in (at, duration) and at > duration: fail(p, 'layer starts outside timeline')


def validate_groups(groups, shots, ref_ids, tolerance, fail, number, text, version=2):
    """Check request membership independently of editorial shot and image counts."""
    if not isinstance(groups, list) or not groups:
        fail('generation_groups', 'nonempty list required for version 2')
        return
    by_id = {s['id']: s for s in shots if isinstance(s, dict) and isinstance(s.get('id'), str)}
    ordered_ids = [s['id'] for s in shots if isinstance(s, dict) and isinstance(s.get('id'), str)]
    assigned, group_ids, requested_by_id = [], set(), {}
    for i, group in enumerate(groups):
        p = f'generation_groups[{i}]'
        if not isinstance(group, dict):
            fail(p, 'expected an object'); continue
        for key in ('id', 'reason', 'continuity'):
            text(group, key, p)
        gid = group.get('id')
        if isinstance(gid, str):
            if gid in group_ids: fail(p + '.id', 'duplicate generation group id')
            group_ids.add(gid)
        requested = number(group.get('requested_duration'), p + '.requested_duration', True)
        if 'continues_from' in group:
            # A continuation reuses the tail of an earlier, accepted request as its reference.
            link = group['continues_from']
            if version != 3: fail(p + '.continues_from', 'use version 3 for continuations')
            elif not isinstance(link, dict): fail(p + '.continues_from', 'expected an object')
            else:
                if link.get('group') not in requested_by_id:
                    fail(p + '.continues_from.group', 'must name an earlier generation group')
                tail = number(link.get('tail'), p + '.continues_from.tail', True)
                earlier = requested_by_id.get(link.get('group'))
                if None not in (tail, earlier) and tail > earlier + tolerance:
                    fail(p + '.continues_from.tail', 'longer than the earlier request')
        if isinstance(gid, str): requested_by_id[gid] = requested
        members = group.get('shot_ids')
        if not isinstance(members, list) or not members or any(not isinstance(s, str) or not s.strip() for s in members):
            fail(p + '.shot_ids', 'nonempty ordered list of shot IDs required')
            members = []
        for sid in members:
            if sid not in by_id: fail(p + '.shot_ids', 'unknown shot ' + sid)
            if sid in assigned: fail(p + '.shot_ids', 'shot assigned more than once ' + sid)
            assigned.append(sid)
        bindings = group.get('bindings')
        if not isinstance(bindings, list) or any(not isinstance(b, str) for b in bindings):
            fail(p + '.bindings', 'expected an ordered list of reference IDs')
        else:
            if len(set(bindings)) != len(bindings): fail(p + '.bindings', 'duplicate binding')
            for binding in bindings:
                if binding not in ref_ids: fail(p + '.bindings', 'unknown reference ' + binding)
        if group.get('provider_prompt') is not None and (not isinstance(group['provider_prompt'], str) or not group['provider_prompt'].strip()):
            fail(p + '.provider_prompt', 'expected nonempty text or null while pending')
        if not members or any(s not in by_id for s in members):
            continue
        selected = [by_id[s] for s in members]
        # Planned request duration must cover its timeline span. Actual source
        # ranges after generation are checked separately by each shot's clip.
        start = number(selected[0].get('start'), p + '.first_shot.start')
        end = number(selected[-1].get('end'), p + '.last_shot.end')
        if None not in (start, end, requested) and requested + tolerance < end - start:
            fail(p + '.requested_duration', f'{requested:g}s cannot cover the {end - start:g}s timeline span')
        for shot in selected:
            required = shot.get('bindings')
            if isinstance(bindings, list) and isinstance(required, list):
                if any(b not in bindings for b in required):
                    fail(p + '.bindings', 'missing a member shot reference binding')
        # One selected result supplies a group; repeated timeline uses must
        # not silently point to different files or different source lengths.
        clips = [s['clip'] for s in selected if isinstance(s.get('clip'), dict)
                 and not (version == 3 and 'repair' in s['clip'])]
        if clips:
            asset = clips[0].get('asset')
            total = number(clips[0].get('duration'), p + '.clip.duration', True)
            for clip in clips[1:]:
                if clip.get('asset') != asset:
                    fail(p, 'member clips must use the same selected source asset')
                other = number(clip.get('duration'), p + '.clip.duration', True)
                if None not in (total, other) and abs(total - other) > tolerance:
                    fail(p, 'member clips must agree on total source duration')
    if assigned != ordered_ids:
        fail('generation_groups', 'groups must cover every shot exactly once in timeline order without interleaving')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text())
        errors = validate(plan)
    except (OSError, ValueError) as exc:
        parser.exit(2, f'Cannot read plan: {exc}\n')
    print(json.dumps({'valid': not errors, 'errors': errors,
                      'scope': 'Structure and timing only; creative review is separate.'}, indent=2))
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()
