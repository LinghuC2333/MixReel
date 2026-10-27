#!/usr/bin/env python3
"""Install all MixReel skills together without overwriting existing skills or reading keys."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile

from check_package import MANIFEST, check_collection

SOURCE = Path(__file__).resolve().parents[1] / 'skills'


def install(destination, source=SOURCE):
    source = Path(source).resolve()
    errors = check_collection(source)
    if errors:
        raise ValueError('Invalid collection: ' + '; '.join(errors))
    destination = Path(destination).expanduser().absolute()
    if any(p.is_symlink() for p in (destination, *destination.parents)):
        raise ValueError('Destination must not contain symlinks')
    if destination.resolve().is_relative_to(source):
        raise ValueError('Destination must be outside collection source')
    names = json.loads((source / MANIFEST).read_text())['skills']
    targets = [*names, MANIFEST]
    if any((destination / n).exists() or (destination / n).is_symlink() for n in targets):
        raise ValueError('MixReel already exists here; choose a new destination and review replacement separately')
    destination.mkdir(parents=True, exist_ok=True)
    # Stage and verify before exposing the installed directories. Roll back only
    # entries created by this call if installation cannot be completed.
    published = []
    with tempfile.TemporaryDirectory(prefix='.mixreel-install-', dir=destination) as temp:
        staging = Path(temp)
        for name in names:
            shutil.copytree(source / name, staging / name,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        shutil.copy2(source / MANIFEST, staging / MANIFEST)
        errors = check_collection(staging)
        if errors:
            raise ValueError('Staged collection invalid: ' + '; '.join(errors))
        try:
            for name in targets:
                target = destination / name
                if name == MANIFEST:
                    with target.open('xb') as out:
                        published.append(target)
                        out.write((staging / name).read_bytes())
                else:
                    # mkdir fails rather than overwriting if another installer wins.
                    target.mkdir()
                    published.append(target)
                    shutil.copytree(staging / name, target, dirs_exist_ok=True)
        except Exception:
            for target in reversed(published):
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            raise
    return {'installed': names, 'destination': str(destination), 'network_requests': 0}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destination', type=Path, required=True,
                   help='Agent skills directory; existing MixReel files are never overwritten')
    args = p.parse_args()
    try:
        result = install(args.destination)
    except (ValueError, OSError) as exc:
        p.exit(1, str(exc) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
