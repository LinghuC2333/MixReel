#!/usr/bin/env python3
"""Write a sanitized JSON copy. Does not audit prose, binaries or unknown secrets."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

REDACTED = '<REDACTED>'
SECRET_KEY = re.compile(r'(?:authorization|api[_-]?key|token|secret|password|credential|signature|signed[_-]?url|presigned)', re.I)
SIGNED_PARAM = re.compile(r'^(?:x-amz-.+|x-goog-.+|signature|sig|token|access_token|api[_-]?key|key-pair-id|policy|credential|se|sp|sv)$', re.I)
URL = re.compile(r'https?://[^\s<>"\x27]+', re.I)
BEARER = re.compile(r'\bBearer\s+[^\s"\x27<>]+', re.I)


def clean_url(match):
    url = match.group(0)
    try:
        parts = urlsplit(url)
        if parts.username or parts.password or any(SIGNED_PARAM.match(k) for k, _ in parse_qsl(parts.query)):
            return REDACTED
        # Query credentials may also be in a URL fragment.
        if any(SIGNED_PARAM.match(k) for k, _ in parse_qsl(parts.fragment)):
            return REDACTED
    except ValueError:
        return REDACTED
    return url


def redact(value):
    if isinstance(value, dict):
        return {k: REDACTED if SECRET_KEY.search(k) else redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        return BEARER.sub('Bearer ' + REDACTED, URL.sub(clean_url, value))
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    if args.source.resolve() == args.destination.resolve():
        parser.error('source and destination must differ')
    data = json.loads(args.source.read_text())
    with args.destination.open('x') as out:
        json.dump(redact(data), out, ensure_ascii=False, indent=2, allow_nan=False)
        out.write('\n')
    print('Sanitized copy written; inspect before sharing.')


if __name__ == '__main__':
    main()
