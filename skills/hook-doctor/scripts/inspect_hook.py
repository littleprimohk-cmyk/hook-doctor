#!/usr/bin/env python3
"""Extract timestamped hook frames and optional audio using Python stdlib + FFmpeg."""
import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys


def run(args):
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('output', type=Path, help='New output directory; existing nonempty directory is rejected')
    parser.add_argument('--seconds', type=float, default=5.0)
    parser.add_argument('--step', type=float, default=0.5)
    parser.add_argument('--audio', action='store_true')
    parser.add_argument('--ffmpeg', default='ffmpeg', help='Executable name or discovered local path')
    args = parser.parse_args()
    if not args.video.is_file():
        parser.error('Video does not exist')
    if not all(math.isfinite(v) and v > 0 for v in (args.seconds, args.step)):
        parser.error('seconds and step must be finite and positive')
    if args.seconds / args.step > 1000:
        parser.error('More than 1000 samples requested; use a larger step')
    executable = shutil.which(args.ffmpeg)
    if not executable:
        parser.error('FFmpeg unavailable; discover/install a trusted FFmpeg or pass --ffmpeg PATH')
    out = args.output.resolve()
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        parser.error('Use a fresh, empty output directory to avoid overwriting assets')
    out.mkdir(parents=True, exist_ok=True)
    video = args.video.resolve()
    probe = run([executable, '-hide_banner', '-i', str(video)])
    # FFmpeg exits nonzero when used without an output; its stderr contains metadata.
    (out / 'metadata.txt').write_text(probe.stderr, encoding='utf-8')
    manifest = {'source': str(video), 'requested_seconds': args.seconds, 'step': args.step,
                'frames': [], 'warnings': [], 'audio': None}
    times = [round(i * args.step, 6) for i in range(int(args.seconds / args.step) + 1)]
    if times[-1] < args.seconds:
        times.append(args.seconds)
    for stamp in times:
        name = f'frame-{stamp:010.6f}s.jpg'
        target = out / name
        result = run([executable, '-hide_banner', '-loglevel', 'error', '-i', str(video),
                      '-ss', str(stamp), '-map', '0:v:0', '-frames:v', '1', '-pix_fmt', 'yuvj420p', '-q:v', '2',
                      '-n', str(target)])
        if result.returncode != 0:
            raise RuntimeError(f'Frame extraction at {stamp}s failed: {result.stderr.strip()}')
        if not target.exists() or target.stat().st_size == 0:
            manifest['warnings'].append(f'No frame at {stamp}s; likely at/past end of media')
            break
        manifest['frames'].append({'requested_time_seconds': stamp, 'file': name})
    if not manifest['frames']:
        raise RuntimeError('No video frames extracted; inspect metadata.txt')
    if args.audio:
        target = out / 'hook-audio.wav'
        result = run([executable, '-hide_banner', '-loglevel', 'error', '-i', str(video),
                      '-t', str(args.seconds), '-vn', '-ac', '1', '-ar', '16000',
                      '-c:a', 'pcm_s16le', '-n', str(target)])
        if result.returncode == 0 and target.exists() and target.stat().st_size > 44:
            manifest['audio'] = target.name
        else:
            manifest['warnings'].append('Audio unavailable; continue with frames and visible captions')
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'output': str(out), 'frame_count': len(manifest['frames']),
                      'warnings': manifest['warnings']}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
