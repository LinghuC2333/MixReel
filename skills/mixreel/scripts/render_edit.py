#!/usr/bin/env python3
"""Render the plan's edit: trim each shot's clip, apply speed and optional frame holds, cut or dissolve, lay the music.

Reads shot.clip {asset, in, duration, speed} and shot.transition from a plan that passes validate_plan.py.
Asset paths are relative to the plan file. Writes a quality master and, optionally, a mobile preview.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent


def load_validator():
    spec = importlib.util.spec_from_file_location('validate_plan', HERE / 'validate_plan.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module.validate


def width(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width',
                          '-of', 'csv=p=0', str(path)], check=True, capture_output=True, text=True).stdout
    return int(out.strip())


def build(plan, base, size, fps, holds):
    shots = plan['shots']
    if any('clip' not in s for s in shots):
        raise ValueError('every shot needs clip {asset, in, duration, speed} before rendering')
    w, h = size
    inputs, graph = [], []
    for i, shot in enumerate(shots):
        clip = shot['clip']
        source = base / clip['asset']
        if not source.is_file(): raise ValueError(f'missing clip for {shot["id"]}: {clip["asset"]}')
        inputs += ['-i', str(source)]
        speed = clip['speed']
        pad = shot.get('transition', {}).get('duration', 0) or 0
        length = shot['end'] - shot['start'] + pad
        cadence = f'fps={holds}:round=near,fps={fps},' if holds else f'fps={fps},'
        sharpen = ',unsharp=5:5:0.7:5:5:0.0' if width(source) < w else ''
        graph.append(f'[{i}:v]trim=start={clip["in"]:.3f}:duration={length * speed:.3f},setpts=(PTS-STARTPTS)/{speed},'
                     f'{cadence}scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h}{sharpen},'
                     f'setsar=1,format=yuv420p,settb=AVTB[v{i}]')
    current = 'v0'
    for i in range(1, len(shots)):
        t = shots[i].get('transition', {'type': 'cut', 'duration': 0})
        nxt = f'c{i}'
        if t.get('type') == 'dissolve':
            graph.append(f'[{current}][v{i}]xfade=transition=fade:duration={t["duration"]}:offset={shots[i]["start"] - t["duration"]:.3f}[{nxt}]')
        else:
            graph.append(f'[{current}][v{i}]concat=n=2:v=1:a=0,settb=AVTB[{nxt}]')
        current = nxt
    music = plan['music']
    total = plan['duration']
    inputs += ['-ss', f'{music["offset"]:.3f}', '-i', str(base / music['asset'])]
    graph.append(f'[{len(shots)}:a]atrim=duration={total:.3f},afade=t=out:st={max(0, total - 0.3):.3f}:d=0.3[aout]')
    return inputs, ';'.join(graph), current, total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('master', type=Path)
    parser.add_argument('--preview', type=Path, help='optional mobile preview path')
    parser.add_argument('--size', default='1080x1920')
    parser.add_argument('--holds', type=float, help='distinct drawings per second, e.g. 12 for frame holds at 24 fps')
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    errors = load_validator()(plan)
    if errors:
        parser.exit(2, 'plan is invalid:\n' + '\n'.join(errors) + '\n')
    for target in (args.master, args.preview):
        if target and target.exists(): parser.exit(2, f'refusing to overwrite {target}\n')
    size = tuple(int(x) for x in args.size.lower().split('x'))
    try:
        inputs, graph, vout, total = build(plan, args.plan.resolve().parent, size, plan['fps'], args.holds)
    except (KeyError, ValueError) as exc:
        parser.exit(2, f'{exc}\n')
    subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', *inputs, '-filter_complex', graph, '-map', f'[{vout}]', '-map', '[aout]',
                    '-r', str(plan['fps']), '-t', f'{total:.3f}', '-c:v', 'libx264', '-crf', '16', '-preset', 'slow',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', str(args.master)], check=True)
    if args.preview:
        subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', str(args.master), '-c:v', 'libx264', '-crf', '21',
                        '-preset', 'slow', '-maxrate', '10M', '-bufsize', '20M', '-c:a', 'copy', str(args.preview)], check=True)
    print(json.dumps({'master': str(args.master), 'preview': str(args.preview) if args.preview else None,
                      'duration': total, 'holds': args.holds}, indent=2))


if __name__ == '__main__':
    main()
