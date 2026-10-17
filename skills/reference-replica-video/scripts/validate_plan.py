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
    if plan.get('version') != 1:
        fail('version', 'unsupported or missing version')
    duration = number(plan.get('duration'), 'duration', True)
    fps = number(plan.get('fps'), 'fps', True)
    tolerance = 0.5 / fps if fps else 0.001
    music = plan.get('music', {})
    if not isinstance(music, dict):
        music = {}; fail('music', 'expected an object')
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
        if not isinstance(kfs, list) or not kfs or any(not isinstance(k, str) or not k for k in kfs):
            fail(p + '.keyframes', 'nonempty list of image IDs required')
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
                    fail(p + '.clip', 'source clip lacks requested range or transition handle')
        if end is not None: previous_end = end
        if length is not None: previous_length = length
    if duration is not None and abs(previous_end - duration) > tolerance:
        fail('shots', 'timeline does not end at target duration')
    count = plan.get('illustration_count')
    if isinstance(count, bool) or not isinstance(count, int) or count != len(frame_ids):
        fail('illustration_count', f'expected {len(frame_ids)} unique images')
    return errors


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
