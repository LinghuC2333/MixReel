#!/usr/bin/env python3
"""Render the plan's edit: trim each shot's clip, apply speed and optional frame holds, cut or dissolve, lay the sound.

Reads shot.clip {asset, in, duration, speed} and shot.transition from a plan that passes validate_plan.py.
Versions 1 and 2 lay the music track only. Version 3 also keeps each shot's sound (its own clip, another
file or silence), overlays edit-layer images or image sequences, adds sound layers, ducks the music and
honours per-shot frame holds. Asset paths are relative to the plan file. Writes a quality master and,
optionally, a mobile preview.
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


def has_audio(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index',
                          '-of', 'csv=p=0', str(path)], check=True, capture_output=True, text=True).stdout
    return bool(out.strip())


def atempo(speed):
    # atempo accepts 0.5 to 2 per stage, so chain stages for larger changes.
    stages = []
    while speed > 2: stages.append('atempo=2'); speed /= 2
    while speed < 0.5: stages.append('atempo=0.5'); speed /= 0.5
    if abs(speed - 1) > 1e-6: stages.append(f'atempo={speed:.6f}')
    return ''.join(',' + x for x in stages)


def build(plan, base, size, fps, holds):
    shots = plan['shots']
    if any('clip' not in s for s in shots):
        raise ValueError('every shot needs clip {asset, in, duration, speed} before rendering')
    v3 = plan.get('version') == 3
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
        shot_holds = shot.get('holds', holds) if v3 else holds
        cadence = f'fps={shot_holds}:round=near,fps={fps},' if shot_holds else f'fps={fps},'
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
    if not v3:
        inputs += ['-ss', f'{music["offset"]:.3f}', '-i', str(base / music['asset'])]
        graph.append(f'[{len(shots)}:a]atrim=duration={total:.3f},afade=t=out:st={max(0, total - 0.3):.3f}:d=0.3[aout]')
        return inputs, ';'.join(graph), current, total
    current = add_overlays(plan, base, size, fps, inputs, graph, current)
    add_sound(plan, base, inputs, graph, total)
    return inputs, ';'.join(graph), current, total


def add_overlays(plan, base, size, fps, inputs, graph, current):
    w, h = size
    for i, overlay in enumerate(plan.get('overlays', [])):
        asset = base / overlay['asset']
        start, end = overlay['start'], overlay['end']
        n = inputs.count('-i')
        if '%' in overlay['asset']:
            inputs += ['-framerate', str(overlay['fps']), '-i', str(asset)]
        elif asset.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp'):
            if not asset.is_file(): raise ValueError(f'missing overlay {overlay["asset"]}')
            inputs += ['-loop', '1', '-t', f'{end - start:.3f}', '-i', str(asset)]
        else:
            if not asset.is_file(): raise ValueError(f'missing overlay {overlay["asset"]}')
            inputs += ['-i', str(asset)]
        graph.append(f'[{n}:v]fps={fps},scale={w}:{h}:flags=lanczos,format=rgba,setpts=PTS-STARTPTS+{start:.3f}/TB[ov{i}]')
        graph.append(f"[{current}][ov{i}]overlay=0:0:eof_action=pass:enable='between(t,{start:.3f},{end:.3f})',format=yuv420p[o{i}]")
        current = f'o{i}'
    return current


def add_sound(plan, base, inputs, graph, total):
    shots, rate = plan['shots'], 48000
    labels = []
    for i, shot in enumerate(shots):
        pad = shot.get('transition', {}).get('duration', 0) or 0
        length = shot['end'] - shot['start'] + pad
        audio = shot.get('audio', {'from': 'clip'})
        n = inputs.count('-i')
        if audio['from'] == 'none':
            inputs += ['-f', 'lavfi', '-t', f'{length:.3f}', '-i', f'anullsrc=r={rate}:cl=stereo']
            graph.append(f'[{n}:a]asetpts=PTS-STARTPTS[a{i}]')
        else:
            src = shot['clip'] if audio['from'] == 'clip' else audio
            path, speed = base / src['asset'], src.get('speed', 1)
            if not has_audio(path):
                raise ValueError(f'{shot["id"]}: {src["asset"]} has no audio; set audio.from to none or another asset')
            inputs += ['-i', str(path)]
            graph.append(f'[{n}:a]atrim=start={src["in"]:.3f}:duration={length * speed:.3f},asetpts=PTS-STARTPTS'
                         f'{atempo(speed)},aresample={rate},aformat=channel_layouts=stereo[a{i}]')
        labels.append(f'a{i}')
    current = labels[0]
    for i in range(1, len(shots)):
        t = shots[i].get('transition', {'type': 'cut', 'duration': 0})
        if t.get('type') == 'dissolve':
            graph.append(f'[{current}][a{i}]acrossfade=d={t["duration"]}[ac{i}]')
        else:
            graph.append(f'[{current}][a{i}]concat=n=2:v=0:a=1[ac{i}]')
        current = f'ac{i}'
    mix = [current]
    music = plan.get('music', {})
    if music.get('source', 'track') == 'track':
        n = inputs.count('-i')
        inputs += ['-ss', f'{music["offset"]:.3f}', '-i', str(base / music['asset'])]
        ducks = plan.get('sound', {}).get('ducking', [])
        expr = '1'
        for d in reversed(ducks):
            expr = f"if(between(t,{d['start']:.3f},{d['end']:.3f}),{d['gain']},{expr})"
        graph.append(f"[{n}:a]atrim=duration={total:.3f},asetpts=PTS-STARTPTS,aresample={rate},aformat=channel_layouts=stereo,"
                     f"volume='{expr}':eval=frame,afade=t=out:st={max(0, total - 0.3):.3f}:d=0.3[music]")
        mix.append('music')
    for i, layer in enumerate(plan.get('sound', {}).get('layers', [])):
        n = inputs.count('-i')
        path = base / layer['asset']
        if not path.is_file(): raise ValueError(f'missing sound layer {layer["asset"]}')
        inputs += ['-i', str(path)]
        delay = int(round(layer['at'] * 1000))
        graph.append(f'[{n}:a]aresample={rate},aformat=channel_layouts=stereo,adelay={delay}|{delay},'
                     f'volume={layer.get("gain", 1)}[layer{i}]')
        mix.append(f'layer{i}')
    graph.append(''.join(f'[{x}]' for x in mix) + f'amix=inputs={len(mix)}:normalize=0:duration=first,'
                 f'atrim=duration={total:.3f},alimiter=limit=0.95[aout]')


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
