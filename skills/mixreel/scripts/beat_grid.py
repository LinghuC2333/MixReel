#!/usr/bin/env python3
"""Fit a regular beat grid to target music and report per-beat kick/hat strength.

Optional dependency: numpy and librosa. A fitted grid is evidence for cut timing,
not proof of where a musical phrase begins; listen around the reported events.
"""
import argparse
import json
from pathlib import Path
import sys


def analyze(path, bpm_hint, bar):
    try:
        import numpy as np
        import librosa
    except ImportError as exc:
        raise RuntimeError('beat_grid requires numpy and librosa; install them or use media_inspect.py audio') from exc
    y, sr = librosa.load(str(path), sr=22050, mono=True)
    duration = len(y) / sr
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    _, frames = librosa.beat.beat_track(onset_envelope=onset, sr=sr, start_bpm=bpm_hint, tightness=200)
    times = librosa.frames_to_time(frames, sr=sr)
    if len(times) < 4:
        raise ValueError('too few beats detected for a grid; the track may not be rhythmic')
    index = np.round((times - times[0]) / np.median(np.diff(times))).astype(int)
    slope, intercept = np.polyfit(index, times, 1)
    period, phase = float(slope), float(intercept % slope)
    residual = float(np.max(np.abs(np.polyval([slope, intercept], index) - times)))
    spec = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
    t = librosa.times_like(spec[0], sr=sr, hop_length=512)

    def band(lo, hi):
        energy = spec[(freqs >= lo) & (freqs < hi)].sum(0)
        rise = np.maximum(0, np.diff(energy, prepend=energy[0]))
        return rise / (rise.max() or 1)

    low, high = band(30, 150), band(1500, 6000)
    rms = librosa.feature.rms(y=y, hop_length=512)[0]
    beats = []
    for i, g in enumerate(np.arange(phase, duration, period)):
        near = (t >= g - 0.06) & (t < g + 0.06)
        span = (t >= g) & (t < g + period)
        db = float(20 * np.log10(rms[span].mean() + 1e-9)) if span.any() else -90.0
        beats.append({'beat': i, 'time': round(float(g), 3), 'kick': round(float(low[near].max()), 2),
                      'hat': round(float(high[near].max()), 2), 'db': round(db, 1), 'bar_start': i % bar == 0})
    return {'source': path.name, 'duration': round(duration, 3), 'bpm': round(60 / period, 2), 'period': round(period, 4),
            'phase': round(phase, 3), 'fit_residual_ms': round(residual * 1000, 1), 'beats': beats,
            'note': 'Grid fit only. Mark drum entry, phrase changes, strongest accents and ending after listening.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('audio', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--bpm', type=float, default=120.0, help='tempo hint for the tracker')
    parser.add_argument('--bar', type=int, default=4, help='beats per bar used only to mark bar starts')
    args = parser.parse_args()
    if not args.audio.is_file():
        parser.exit(2, 'audio must be an existing local file\n')
    try:
        result = analyze(args.audio, args.bpm, args.bar)
    except (RuntimeError, ValueError) as exc:
        parser.exit(2, f'{exc}\n')
    with args.output.open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n')
    strong = sorted(result['beats'], key=lambda b: -b['kick'])[:4]
    print(json.dumps({'output': str(args.output), 'bpm': result['bpm'], 'phase': result['phase'],
                      'fit_residual_ms': result['fit_residual_ms'],
                      'strongest_kicks': sorted(b['time'] for b in strong)}, indent=2))


if __name__ == '__main__':
    sys.exit(main())
