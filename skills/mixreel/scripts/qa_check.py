#!/usr/bin/env python3
"""Quality gate for a finished edit before delivery. Read-only; uses ffmpeg/ffprobe, no network.

With a plan, each planned cut is checked frame by frame: the few frames just before the cut should look
like the outgoing shot and those just after it like the incoming shot. Frames that look like the wrong
side are stray frames, for example a few frames of the next shot left at the end of the previous one.
Picture changes the plan does not explain, such as sparks, fast motion or an unplanned cut, are listed
as candidates for a person to inspect, never judged automatically. Also reports silences, loudness,
true peak, duration and frame size.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess


def run(args):
    return subprocess.run(args, capture_output=True, text=True)


def probe(path):
    out = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height,r_frame_rate',
               '-of', 'json', str(path)])
    if out.returncode:
        raise ValueError(f'cannot read {path}: {out.stderr.strip()}')
    data = json.loads(out.stdout)
    video = next((s for s in data.get('streams', []) if s.get('codec_type') == 'video'), None)
    if not video:
        raise ValueError(f'{path} has no video stream')
    num, den = (int(x) for x in video['r_frame_rate'].split('/'))
    return {'duration': float(data['format']['duration']), 'width': video['width'], 'height': video['height'],
            'fps': num / den if den else 0, 'audio': any(s.get('codec_type') == 'audio' for s in data['streams'])}


def detect_changes(path, threshold):
    err = run(['ffmpeg', '-v', 'info', '-nostdin', '-i', str(path), '-an', '-vf',
               f"select='gt(scene,{threshold})',showinfo", '-f', 'null', '-']).stderr
    return [round(float(t), 3) for t in re.findall(r'pts_time:([0-9.]+)', err)]


def frame(path, at, w=32, h=56):
    """A tiny YUV 4:4:4 frame: luma averaged over 4x4 blocks plus mean chroma."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-ss', f'{max(0, at):.4f}', '-i', str(path),
                          '-frames:v', '1', '-vf', f'scale={w}:{h},format=yuv444p', '-f', 'rawvideo', '-'],
                         capture_output=True).stdout
    n = w * h
    if len(raw) < 3 * n:
        return None
    luma = raw[:n]
    blocks = [sum(luma[(y * 4 + j) * w + x * 4 + i] for j in range(4) for i in range(4)) / 16
              for y in range(h // 4) for x in range(w // 4)]
    return blocks, sum(raw[n:2 * n]) / n, sum(raw[2 * n:]) / n


def likeness(a, b):
    """Higher means more alike: layout correlation, minus penalties for colour and brightness shift."""
    la, lb = a[0], b[0]
    ma, mb = sum(la) / len(la), sum(lb) / len(lb)
    da, db = [x - ma for x in la], [y - mb for y in lb]
    sa, sb = sum(x * x for x in da) ** 0.5, sum(y * y for y in db) ** 0.5
    if sa > 1e-6 and sb > 1e-6:
        corr = sum(x * y for x, y in zip(da, db)) / (sa * sb)
    else:
        corr = 1.0 if abs(ma - mb) < 4 else 0.0
    return corr - (abs(a[1] - b[1]) + abs(a[2] - b[2])) / 64 - abs(ma - mb) / 255


def check_cut(path, cut, fps, window, room_before, room_after):
    """Count frames on each side of a planned cut that resemble the other shot more than their own."""
    before_n = min(window, int(room_before * fps) - 1)
    after_n = min(window, int(room_after * fps) - 1)
    if before_n < 1 or after_n < 1:
        return None
    k = round(cut * fps)
    # Seeking returns the first frame at or after the time, so aim just before frame k + i starts.
    at = lambda i: (k + i - 0.25) / fps
    outgoing, incoming = frame(path, at(-before_n - 1)), frame(path, at(after_n))
    if not outgoing or not incoming:
        return None
    early = late = 0
    for i in range(-before_n, 0):
        f = frame(path, at(i))
        if f and likeness(f, incoming) > likeness(f, outgoing): early += 1
    for i in range(0, after_n):
        f = frame(path, at(i))
        if f and likeness(f, outgoing) > likeness(f, incoming): late += 1
    return {'cut': cut, 'frames_like_next_shot_before_cut': early, 'frames_like_previous_shot_after_cut': late}


def detect_silence(path, noise_db, minimum):
    err = run(['ffmpeg', '-v', 'info', '-nostdin', '-i', str(path), '-vn', '-af',
               f'silencedetect=n={noise_db}dB:d={minimum}', '-f', 'null', '-']).stderr
    starts = [float(x) for x in re.findall(r'silence_start: (-?[0-9.]+)', err)]
    ends = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', err)]
    return [{'start': round(max(0, s), 3), 'end': round(e, 3) if e is not None else None}
            for s, e in zip(starts, ends + [None] * (len(starts) - len(ends)))]


def measure_loudness(path):
    err = run(['ffmpeg', '-v', 'info', '-nostdin', '-i', str(path), '-vn', '-af', 'loudnorm=print_format=json',
               '-f', 'null', '-']).stderr
    block = err[err.rfind('{'):err.rfind('}') + 1]
    try:
        data = json.loads(block)
        return {'integrated_lufs': float(data['input_i']), 'true_peak_db': float(data['input_tp'])}
    except (ValueError, KeyError):
        return None


def check(video, plan=None, threshold=0.3, window=4, size=None, lufs=None, noise_db=-50, min_silence=0.5):
    info = probe(video)
    fps, duration = info['fps'] or 24, info['duration']
    tolerance = 2 / fps
    issues = []
    overlays = [(o['start'], o['end']) for o in (plan or {}).get('overlays', [])]
    covered = lambda t: any(a - tolerance <= t <= b + tolerance for a, b in overlays)

    cut_checks, planned = [], []
    if plan:
        shots = plan.get('shots', [])
        for prev, shot in zip(shots, shots[1:]):
            if shot.get('transition', {}).get('type', 'cut') != 'cut':
                continue
            planned.append(shot['start'])
            if covered(shot['start']):
                continue
            result = check_cut(video, shot['start'], fps, window,
                               shot['start'] - prev['start'], shot['end'] - shot['start'])
            if result:
                cut_checks.append(result)
        stray = [c for c in cut_checks
                 if c['frames_like_next_shot_before_cut'] or c['frames_like_previous_shot_after_cut']]
        if stray:
            issues.append(f'{len(stray)} planned cut(s) with frames from the neighbouring shot')
        if abs(duration - plan.get('duration', duration)) > 1 / fps:
            issues.append(f'duration {duration:.3f}s differs from plan {plan["duration"]}s')

    # Everything the plan does not explain is listed for a person to look at, not judged here.
    changes = [c for c in detect_changes(video, threshold) if not covered(c)]
    unplanned = [c for c in changes if not any(abs(c - t) <= tolerance for t in planned)]
    bounds = [0.0] + changes + [duration]
    short_runs = [{'start': a, 'end': round(b, 3), 'frames': round((b - a) * fps)}
                  for a, b in zip(bounds, bounds[1:]) if 0 < round((b - a) * fps) < window]

    silences, loud = [], None
    if not info['audio']:
        issues.append('no audio stream')
    else:
        silences = detect_silence(video, noise_db, min_silence)
        if silences: issues.append(f'{len(silences)} silence(s) of {min_silence}s or more')
        loud = measure_loudness(video)
        if loud and loud['true_peak_db'] > -1:
            issues.append(f'true peak {loud["true_peak_db"]} dB above -1 dB')
        if loud and lufs is not None and abs(loud['integrated_lufs'] - lufs) > 1.5:
            issues.append(f'loudness {loud["integrated_lufs"]} LUFS, target {lufs}')
    if size and (info['width'], info['height']) != size:
        issues.append(f'frame size {info["width"]}x{info["height"]}, expected {size[0]}x{size[1]}')
    return {'video': str(video), 'duration': round(duration, 3), 'size': f'{info["width"]}x{info["height"]}',
            'fps': round(fps, 3), 'cut_checks': cut_checks, 'unplanned_changes': unplanned,
            'short_runs_between_changes': short_runs, 'silences': silences, 'loudness': loud, 'issues': issues,
            'scope': 'Planned cuts are checked; unplanned changes and short runs are candidates to watch. '
                     'Dialogue placement, gaze and taste need watching and listening.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--plan', type=Path, help='plan.json whose timeline the video follows')
    parser.add_argument('--threshold', type=float, default=0.3, help='scene-change threshold for listing candidates')
    parser.add_argument('--window', type=int, default=4, help='frames checked on each side of a planned cut')
    parser.add_argument('--size', help='expected frame size, e.g. 1080x1920')
    parser.add_argument('--lufs', type=float, help='target integrated loudness for the platform')
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text()) if args.plan else None
        size = tuple(int(x) for x in args.size.lower().split('x')) if args.size else None
        result = check(args.video, plan, args.threshold, args.window, size, args.lufs)
    except (OSError, ValueError) as exc:
        parser.exit(2, f'{exc}\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if result['issues'] else 0)


if __name__ == '__main__':
    main()
