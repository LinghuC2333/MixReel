#!/usr/bin/env python3
"""Offline collection structure, links, syntax and heuristic privacy checks."""
import ast
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'mixreel.collection.json'
LINK = re.compile(r'\[[^\]]*\]\(([^)]+)\)')


def local_links(path):
    for target in LINK.findall(path.read_text()):
        if '://' in target or target.startswith('#'):
            continue
        yield (path.parent / target.split('#')[0]).resolve()


def check_collection(directory):
    directory = Path(directory).resolve()
    errors = []
    try:
        manifest = json.loads((directory / MANIFEST).read_text())
        if not isinstance(manifest, dict):
            raise ValueError('manifest must be an object')
        names = manifest['skills']
        if (manifest.get('version') != 1 or not isinstance(names, list) or not names
                or any(not isinstance(n, str) or not re.fullmatch(r'[a-z0-9-]+', n) for n in names)
                or len(names) != len(set(names)) or manifest.get('core') != 'mixreel'
                or 'mixreel' not in names):
            raise ValueError('invalid collection manifest')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return ['collection manifest missing or invalid: ' + type(exc).__name__]
    roots = [directory / n for n in names]
    entries = []
    for name, root in zip(names, roots):
        entry = root / 'SKILL.md'
        if not entry.is_file():
            errors.append('missing skill entry: ' + name)
            continue
        entries.append(entry)
        text = entry.read_text()
        front = re.match(r'^---\n(.*?)\n---\n', text, re.S)
        if not front or not re.search(r'^name: ' + re.escape(name) + r'$', front[1], re.M):
            errors.append('invalid skill name: ' + name)
        if not front or not re.search(r'^description: .+', front[1], re.M):
            errors.append('missing description: ' + name)
        if len(text.splitlines()) > 150:
            errors.append('entrypoint too large: ' + name)
        metadata = root / 'agents/openai.yaml'
        if not metadata.is_file():
            errors.append('missing agent metadata: ' + name)
        else:
            body = metadata.read_text()
            for field in ('display_name', 'short_description', 'default_prompt'):
                found = re.search(r'^  ' + field + r': (".*")$', body, re.M)
                try:
                    value = json.loads(found[1]) if found else None
                except ValueError:
                    value = None
                if not isinstance(value, str) or not value:
                    errors.append('invalid metadata ' + name + '.' + field)
                elif field == 'short_description' and not 25 <= len(value) <= 64:
                    errors.append('invalid metadata length: ' + name)
                elif field == 'default_prompt' and '$' + name not in value:
                    errors.append('missing invocation in default prompt: ' + name)
    discovered = {p.parent.name for p in directory.glob('*/SKILL.md') if p.parent.name.startswith('mixreel')}
    for name in discovered - set(names):
        errors.append('unlisted skill: ' + name)
    # Every local Markdown dependency must survive copying the collection alone.
    for root in roots:
        for p in root.rglob('*'):
            if p.is_symlink():
                errors.append('symlink in collection: ' + str(p.relative_to(directory)))
            if p.is_file() and p.suffix == '.md':
                for target in local_links(p):
                    if not any(target.is_relative_to(r) for r in roots) or not target.exists():
                        errors.append('broken collection link: ' + str(p.relative_to(directory)))
    reached, queue = set(), list(entries)
    while queue:
        p = queue.pop().resolve()
        if p in reached or not p.is_file() or not any(p.is_relative_to(r) for r in roots):
            continue
        reached.add(p)
        if p.suffix == '.md':
            queue.extend(local_links(p))
    for root in roots:
        for p in (root / 'references').glob('*.md'):
            compatibility = p.read_text().startswith(('# Moved reference\n', '# Video workflow references\n'))
            if p.resolve() not in reached and not compatibility:
                errors.append('unrouted reference: ' + str(p.relative_to(directory)))
    return errors


def check_package(root):
    root = Path(root).resolve()
    errors = check_collection(root / 'skills')
    private_patterns = [r'/Users/' + r'[^/\s]+/', r'https://[^/\s]*' + r'feishu\.cn/',
                        r'(?i)Bearer\s+[A-Za-z0-9_-]{24,}',
                        r'(?i)(?:api_key|api-key|access_token|secret_key)\s*[=:]\s*["\x27]?[A-Za-z0-9_-]{24,}']
    for path in root.rglob('*'):
        if not path.is_file() or any(x in path.parts for x in ('.git', '__pycache__')):
            continue
        if path.name in ('credentials.json', 'providers.json') or path.suffix in ('.key', '.pem'):
            errors.append('private configuration in package: ' + str(path.relative_to(root)))
        if path.name == '.env' or path.name.startswith('.env.') or path.suffix in ('.mp4', '.mp3', '.webp', '.png', '.jpg'):
            errors.append('private/media payload in package: ' + str(path.relative_to(root)))
        if path.suffix not in ('.md', '.py', '.json', '.yaml', '.yml'):
            continue
        text = path.read_text()
        if path.suffix == '.py':
            try:
                ast.parse(text)
            except SyntaxError as exc:
                errors.append(path.name + ': ' + exc.msg)
        if path.suffix == '.json':
            try:
                json.loads(text)
            except ValueError:
                errors.append('invalid JSON: ' + path.name)
        if path.suffix == '.md':
            for actual in local_links(path):
                if not actual.is_relative_to(root) or not actual.exists():
                    errors.append('broken or external local link: ' + str(path.relative_to(root)))
        if path.name != 'check_package.py':
            for pattern in private_patterns:
                if re.search(pattern, text):
                    errors.append('possible private data: ' + str(path.relative_to(root)))
    return errors


def main():
    errors = check_package(ROOT)
    print(json.dumps({'ok': not errors, 'errors': errors,
                      'scope': 'Collection structure, installed-relative links and heuristic privacy scan only'}, indent=2))
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
