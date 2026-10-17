#!/usr/bin/env python3
"""Offline package structure, links, syntax and obvious private-data checks."""
import ast
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/reference-replica-video'
errors=[]
entry=(SKILL/'SKILL.md').read_text()
front=re.match(r'^---\n(.*?)\n---\n',entry,re.S)
if not front or not re.search(r'^name: reference-replica-video$',front[1],re.M):errors.append('invalid skill name')
if not front or not re.search(r'^description: .+',front[1],re.M):errors.append('missing description')
if len(entry.splitlines())>150:errors.append('entrypoint too large; review progressive disclosure')
private_patterns=[r'/Users/' + r'[^/\s]+/', r'https://[^/\s]*' + r'feishu\.cn/',
                  r'(?i)Bearer\s+[A-Za-z0-9_-]{24,}',
                  r'(?i)(?:api_key|api-key|access_token|secret_key)\s*[=:]\s*["\x27]?[A-Za-z0-9_-]{24,}']
for path in ROOT.rglob('*'):
    if not path.is_file() or any(x in path.parts for x in ('.git','__pycache__')):continue
    if path.name in ('credentials.json', 'providers.json') or path.suffix in ('.key', '.pem'):
        errors.append(f'private configuration in package: {path.relative_to(ROOT)}')
    if path.name=='.env' or path.name.startswith('.env.') or path.suffix in ('.mp4','.mp3','.webp','.png','.jpg'):
        errors.append(f'private/media payload in package: {path.relative_to(ROOT)}')
    if path.suffix not in ('.md','.py','.json','.yaml','.yml'):continue
    text=path.read_text()
    if path.suffix=='.py':
        try:ast.parse(text)
        except SyntaxError as exc:errors.append(f'{path.name}: {exc.msg}')
    if path.suffix=='.json':
        try:json.loads(text)
        except ValueError:errors.append(f'invalid JSON: {path.name}')
    if path.suffix=='.md':
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
            if '://' in target or target.startswith('#'):continue
            actual=(path.parent/target.split('#')[0]).resolve()
            if not actual.is_relative_to(ROOT.resolve()) or not actual.exists():
                errors.append(f'broken or external local link: {path.name} -> {target}')
    if path.name!='check_package.py':
        for pattern in private_patterns:
            if re.search(pattern,text):errors.append(f'possible private data: {path.relative_to(ROOT)}')
for ref in (SKILL/'references').glob('*.md'):
    if f'references/{ref.name}' not in entry:errors.append(f'unrouted reference: {ref.name}')
print(json.dumps({'ok':not errors,'errors':errors,'scope':'Structural checks and heuristic privacy scan only'},indent=2))
sys.exit(bool(errors))
