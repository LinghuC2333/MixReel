#!/usr/bin/env python3
"""Create blank local configuration without reading keys or contacting a provider."""
import argparse
import json
import os
from pathlib import Path
import stat

SKILL = Path(__file__).resolve().parents[1]


def initialize(directory):
    directory = Path(directory).expanduser().absolute()
    # Never follow a symlink into an unexpected configuration location.
    for part in (directory, *directory.parents):
        if part.is_symlink():
            raise ValueError('Configuration path contains a symlink')
    resolved = directory.resolve()
    if resolved.is_relative_to(SKILL):
        raise ValueError('Configuration must be outside the installed skill')
    for parent in (resolved, *resolved.parents):
        if (parent / '.git').exists():
            raise ValueError('Configuration must be outside Git repositories')
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name == 'posix':
        info = directory.stat()
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
            raise ValueError('Configuration directory must be user-owned with mode 700')
    results = {}
    for name in ('providers', 'credentials'):
        target = directory / (name + '.json')
        if target.is_symlink():
            raise ValueError('Configuration file must not be a symlink')
        if target.exists():
            if not target.is_file():
                raise ValueError('Configuration target must be a regular file')
            if os.name == 'posix':
                info = target.stat()
                if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
                    raise ValueError('Existing configuration file must have mode 600')
            results[name] = 'preserved'
            continue
        content = (SKILL / 'assets' / (name + '.example.json')).read_bytes()
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
        try:
            fd = os.open(target, flags, 0o600)
        except FileExistsError:
            raise ValueError('Configuration changed concurrently; retry initialization') from None
        with os.fdopen(fd, 'wb') as stream:
            stream.write(content)
        results[name] = 'created_blank'
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path,
                        default=Path.home() / '.config' / 'reference-replica-video')
    args = parser.parse_args()
    try:
        results = initialize(args.directory)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'Configuration initialization failed: {exc}\n')
    print(json.dumps({'directory': str(args.directory.expanduser()), 'files': results,
                      'network_requests': 0, 'keys_imported': 0}))
    if os.name != 'posix':
        print('Set directory access to your user only using the operating-system ACL.')


if __name__ == '__main__':
    main()
