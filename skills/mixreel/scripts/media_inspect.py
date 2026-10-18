#!/usr/bin/env python3
"""Local reference frames, audio diagnostics and motion-change candidates. Requires ffmpeg."""
import argparse
from array import array
import json
import math
from pathlib import Path
import re
import subprocess
import sys


def run(args):
    return subprocess.run(args, check=True, capture_output=True)


def probe(path):
    if not path.is_file(): raise ValueError('input must be an existing local file')
    result = json.loads(run(['ffprobe', '-v', 'error', '-protocol_whitelist', 'file,pipe',
                             '-show_format', '-show_streams', '-of', 'json', str(path)]).stdout)
    duration = float(result['format']['duration'])
    if not math.isfinite(duration) or duration <= 0 or duration > 600:
        raise ValueError('diagnostic input must have a known duration between 0 and 600 seconds')
    return result, duration


def ffinput(path):
    return ['ffmpeg', '-v', 'error', '-nostdin', '-protocol_whitelist', 'file,pipe', '-i', str(path)]


def write_new(path, value):
    with path.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False); f.write('\n')


def peaks(values, spacing, count):
    chosen = []
    for i in sorted(range(len(values)), key=lambda j: values[j], reverse=True):
        if values[i] <= 0: break
        if all(abs(i - x) >= spacing for x in chosen): chosen.append(i)
        if len(chosen) >= count: break
    return sorted(chosen)


def reference(path, out, interval, threshold):
    meta, duration = probe(path)
    if not any(s['codec_type'] == 'video' for s in meta['streams']): raise ValueError('no video stream')
    if math.ceil(duration / interval) > 240: raise ValueError('too many preview frames; increase --interval')
    out.mkdir(parents=True, exist_ok=False)
    command = ffinput(path)
    command[2] = 'info'
    log = run(command + ['-an', '-vf', f"select='gt(scene,{threshold})',showinfo", '-f', 'null', '-']).stderr.decode(errors='replace')
    cuts = sorted(set(float(x) for x in re.findall(r'pts_time:([0-9.]+)', log)))
    cuts = [x for x in cuts if 0 < x < duration]
    bounds = [0.0, *cuts, duration]
    run(ffinput(path) + ['-an', '-vf', f'fps=1/{interval},scale=320:-2', '-frames:v', '240', str(out/'frame_%04d.jpg')])
    frames = sorted(out.glob('frame_*.jpg'))
    # fps samples are approximate representatives of interval bins, not exact shot boundaries.
    frame_index = [{'file': f.name, 'approx_time': round(i * interval, 3)} for i, f in enumerate(frames)]
    cols = 6; rows = math.ceil(len(frames) / cols)
    if rows:
        run(['ffmpeg', '-v', 'error', '-nostdin', '-framerate', '1', '-i', str(out/'frame_%04d.jpg'),
             '-vf', f'tile={cols}x{rows}', '-frames:v', '1', str(out/'contact.jpg')])
    result = {'duration': duration, 'source': path.name, 'scene_threshold': threshold,
              'cut_candidates': cuts, 'shots': [{'start': a, 'end': b} for a,b in zip(bounds,bounds[1:])],
              'frames': frame_index, 'note': 'Automated candidates; inspect actual video for camera motion and dissolves.'}
    write_new(out/'analysis.json', result)
    return result


def audio(path, out):
    meta, duration = probe(path)
    if not any(s['codec_type'] == 'audio' for s in meta['streams']): raise ValueError('no audio stream')
    raw = run(ffinput(path) + ['-vn', '-ac', '1', '-ar', '8000', '-f', 's16le', '-']).stdout
    samples = array('h'); samples.frombytes(raw)
    if sys.byteorder != 'little': samples.byteswap()
    step = 160  # 20 ms RMS windows
    rms = []
    for i in range(0, len(samples), step):
        window = samples[i:i+step]
        rms.append(math.sqrt(sum(x*x for x in window) / len(window)) / 32768)
    changes = [max(0.0, r - (rms[i-1] if i else 0.0)) for i, r in enumerate(rms)]
    silence = []; start = None
    for i, value in enumerate([*rms, 1.0]):
        if value < 10**(-50/20) and start is None: start = i * .02
        elif value >= 10**(-50/20) and start is not None:
            if i * .02 - start >= .25: silence.append({'start': round(start, 3), 'end': round(min(i*.02, duration),3)})
            start = None
    result = {'duration': duration, 'source': path.name, 'window_seconds': .02,
              'silence_candidates': silence,
              'onset_candidates': [{'time': round(i*.02, 3), 'strength': changes[i]} for i in peaks(changes, 10, 32)],
              'note': 'Energy changes are not a beat grid or phrase analysis. Listen and verify.'}
    write_new(out, result); return result


def motion(path, out, fps):
    meta, duration = probe(path)
    if not any(s['codec_type'] == 'video' for s in meta['streams']): raise ValueError('no video stream')
    w, h = 64, 112
    raw = run(ffinput(path) + ['-an', '-vf', f'fps={fps},scale={w}:{h},format=gray', '-f', 'rawvideo', '-']).stdout
    size = w*h; values = []
    for i in range(size, len(raw), size):
        before, after = raw[i-size:i], raw[i:i+size]
        if len(after) == size: values.append(sum(abs(a-b) for a,b in zip(before,after))/size)
    result = {'duration': duration, 'source': path.name, 'fps': fps,
              'change_candidates': [{'time': round((i+1)/fps, 4), 'difference': values[i]} for i in peaks(values, max(1,int(fps*.2)), 10)],
              'curve': [{'time': round((i+1)/fps, 4), 'difference': v} for i,v in enumerate(values)],
              'note': 'Camera motion, flashes and defects also create peaks. Confirm narrative events visually.'}
    write_new(out, result); return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    for name in ('reference', 'audio', 'motion'):
        sp = sub.add_parser(name); sp.add_argument('source', type=Path); sp.add_argument('output', type=Path)
        if name == 'reference':
            sp.add_argument('--interval', type=float, default=.5); sp.add_argument('--threshold', type=float, default=.3)
        if name == 'motion': sp.add_argument('--fps', type=int, default=12)
    a = p.parse_args()
    try:
        if a.command == 'reference':
            if not math.isfinite(a.interval) or a.interval <= 0 or not 0 < a.threshold < 1: raise ValueError('invalid sampling settings')
            result = reference(a.source, a.output, a.interval, a.threshold)
        elif a.command == 'audio': result = audio(a.source, a.output)
        else:
            if not 1 <= a.fps <= 60: raise ValueError('fps must be 1 through 60')
            result = motion(a.source, a.output, a.fps)
        print(json.dumps({'output': str(a.output), 'duration': result['duration']}))
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        # Avoid dumping ffmpeg output containing private paths or metadata.
        p.exit(2, f'Inspection failed ({type(exc).__name__}): check local media and output path.\n')


if __name__ == '__main__':
    main()
