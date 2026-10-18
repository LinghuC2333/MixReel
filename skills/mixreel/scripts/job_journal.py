#!/usr/bin/env python3
"""Local budget reservations and job recovery. Never calls a provider or submits work."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

STATES = {
    'prepared': {'submitting', 'cancelled'},
    'submitting': {'submitted', 'outcome_unknown', 'generation_succeeded', 'failed'},
    'outcome_unknown': {'submitted', 'generation_succeeded', 'failed'},
    'submitted': {'generation_succeeded', 'failed', 'outcome_unknown'},
    'generation_succeeded': {'downloaded'},
    'downloaded': set(), 'failed': set(), 'cancelled': set(),
}


def amount(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('invalid monetary amount') from exc
    if not result.is_finite() or result < 0:
        raise ValueError('amount must be finite and nonnegative')
    return result


def now():
    return datetime.now(timezone.utc).isoformat()


def fingerprint(request, provider, model, operation):
    encoded = json.dumps({'request': request, 'provider': provider, 'model': model,
                          'operation': operation}, sort_keys=True, separators=(',', ':'),
                         allow_nan=False).encode()
    return hashlib.sha256(encoded).hexdigest()


@contextmanager
def locked(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_suffix(path.suffix + '.lock')
    fd = os.open(lock, os.O_RDWR | os.O_CREAT, 0o600)
    with os.fdopen(fd, 'r+b') as handle:
        if os.name == 'nt':
            import msvcrt
            if os.fstat(handle.fileno()).st_size == 0:
                handle.write(b'0'); handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == 'nt':
                handle.seek(0); msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def save(path, data):
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def exposure(data, currency):
    return sum((amount(j['billed'] if j['billed'] is not None else j['reserved'])
                for j in data['jobs'].values() if j['currency'] == currency), Decimal(0))


def report(data):
    totals = {}
    for currency, cap in data['budgets'].items():
        jobs = [j for j in data['jobs'].values() if j['currency'] == currency]
        billed = sum((amount(j['billed']) for j in jobs if j['billed'] is not None), Decimal(0))
        exp = exposure(data, currency)
        totals[currency] = {'budget': cap, 'billed': str(billed),
                            'reserved_unreconciled': str(exp - billed),
                            'remaining': str(amount(cap) - exp),
                            'unreconciled_jobs': sum(j['billed'] is None for j in jobs)}
        totals[currency]['billed_by_use'] = {
            use: str(sum((amount(j['billed']) for j in jobs
                          if j['billed'] is not None and j['use'] == use), Decimal(0)))
            for use in ('retained', 'shared', 'discarded', 'undecided')}
    return {'totals': totals, 'jobs': {k: {'state': v['state'], 'task_id': v['task_id'],
                                        'billing_known': v['billed'] is not None}
                                     for k, v in data['jobs'].items()}}


def reserve(data, job_id, request, provider, model, operation, currency, ceiling,
            evidence, quote=None, quote_kind='unavailable', repeat_reason=None):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', job_id): raise ValueError('invalid job id')
    if job_id in data['jobs']: raise ValueError('job already exists; inspect its state')
    if currency not in data['budgets']: raise ValueError('no budget in this currency')
    if not all(isinstance(x, str) and x.strip() for x in (provider, model, operation, evidence)):
        raise ValueError('provider, model, operation and authorization evidence required')
    ceiling = amount(ceiling)
    if ceiling <= 0: raise ValueError('positive maximum charge required')
    if quote_kind not in ('quoted', 'estimated', 'unavailable'): raise ValueError('invalid quote kind')
    if quote_kind == 'unavailable' and quote is not None: raise ValueError('unavailable quote must be null')
    if quote_kind != 'unavailable' and quote is None: raise ValueError('missing quote amount')
    if quote is not None and amount(quote) > ceiling: raise ValueError('quote exceeds authorized maximum')
    digest = fingerprint(request, provider, model, operation)
    for old in data['jobs'].values():
        if old['request_hash'] != digest: continue
        if old['state'] in ('submitting', 'outcome_unknown', 'submitted'):
            raise ValueError('matching submission unresolved; reconcile before retry')
        if not repeat_reason or not repeat_reason.strip():
            raise ValueError('matching request exists; intentional variation needs repeat reason')
    if exposure(data, currency) + ceiling > amount(data['budgets'][currency]):
        raise ValueError('reservation exceeds remaining budget')
    data['jobs'][job_id] = {
        'provider': provider, 'model': model, 'operation': operation,
        'request_hash': digest, 'currency': currency, 'reserved': str(ceiling),
        'quote': str(amount(quote)) if quote is not None else None, 'quote_kind': quote_kind,
        'billed': None, 'billing_evidence': None, 'state': 'prepared', 'task_id': None,
        'authorization_evidence': evidence, 'repeat_reason': repeat_reason,
        'artifact': None, 'use': 'undecided',
        'history': [{'at': now(), 'state': 'prepared', 'evidence': evidence}],
    }


def transition(data, job_id, state, evidence, task_id=None, artifact=None):
    job = data['jobs'][job_id]
    if state not in STATES.get(job['state'], set()): raise ValueError('invalid state transition')
    if not evidence.strip(): raise ValueError('transition evidence required')
    if state == 'submitted' and not (task_id or job['task_id']):
        raise ValueError('submitted state requires provider task id')
    if task_id:
        if job['task_id'] and task_id != job['task_id']: raise ValueError('task id cannot change')
    artifact_record = None
    if state == 'downloaded':
        if not artifact: raise ValueError('downloaded state requires a local artifact')
        path = Path(artifact)
        if not path.is_file() or path.stat().st_size == 0: raise ValueError('artifact missing or empty')
        h = hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
        artifact_record = {'path': str(path.resolve()), 'sha256': h.hexdigest(), 'bytes': path.stat().st_size}
    job['state'] = state
    if task_id: job['task_id'] = task_id
    if artifact_record: job['artifact'] = artifact_record
    if state == 'cancelled':
        job['billed'] = '0'; job['billing_evidence'] = 'Cancelled before submission; ' + evidence
    job['history'].append({'at': now(), 'state': state, 'evidence': evidence})


def reconcile(data, job_id, billed, evidence):
    job = data['jobs'][job_id]
    if job['state'] not in ('generation_succeeded', 'downloaded', 'failed'):
        raise ValueError('reconcile final billing only after terminal generation status')
    if not evidence.strip(): raise ValueError('billing evidence required')
    value = str(amount(billed))
    job['billed'] = value
    job['billing_evidence'] = evidence
    job['history'].append({'at': now(), 'billed': value, 'evidence': evidence})
    # Actual charges above the ceiling must remain visible rather than being rejected.


def classify(data, job_id, use, evidence):
    if use not in ('retained', 'shared', 'discarded', 'undecided') or not evidence.strip():
        raise ValueError('valid use and evidence required')
    job = data['jobs'][job_id]
    job['use'] = use
    job['history'].append({'at': now(), 'use': use, 'evidence': evidence})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init'); init.add_argument('journal', type=Path)
    init.add_argument('--budget', action='append', required=True, help='CURRENCY=maximum, repeatable')
    prep = sub.add_parser('prepare'); prep.add_argument('journal', type=Path)
    for key in ('job', 'request', 'provider', 'model', 'operation', 'currency', 'reserve', 'evidence'):
        prep.add_argument('--' + key, required=True)
    prep.add_argument('--quote'); prep.add_argument('--quote-kind', default='unavailable', choices=['quoted', 'estimated', 'unavailable'])
    prep.add_argument('--repeat-reason')
    move = sub.add_parser('transition'); move.add_argument('journal', type=Path)
    move.add_argument('--job', required=True); move.add_argument('--state', choices=STATES, required=True)
    move.add_argument('--evidence', required=True); move.add_argument('--task-id'); move.add_argument('--artifact')
    bill = sub.add_parser('bill'); bill.add_argument('journal', type=Path)
    for key in ('job', 'amount', 'evidence'): bill.add_argument('--' + key, required=True)
    cl = sub.add_parser('classify'); cl.add_argument('journal', type=Path)
    for key in ('job', 'use', 'evidence'): cl.add_argument('--' + key, required=True)
    show = sub.add_parser('report'); show.add_argument('journal', type=Path)
    args = p.parse_args()
    try:
        with locked(args.journal):
            if args.command == 'init':
                if args.journal.exists(): raise ValueError('journal exists; refusing overwrite')
                budgets = {}
                for item in args.budget:
                    c, v = item.split('=', 1)
                    if not re.fullmatch('[A-Z]{3}', c) or c in budgets: raise ValueError('invalid or duplicate currency')
                    budgets[c] = str(amount(v))
                data = {'version': 1, 'budgets': budgets, 'jobs': {}}
            else:
                data = json.loads(args.journal.read_text())
                if data.get('version') != 1: raise ValueError('unsupported journal version')
            if args.command == 'prepare':
                request = json.loads(Path(args.request).read_text())
                reserve(data, args.job, request, args.provider, args.model, args.operation, args.currency,
                        args.reserve, args.evidence, args.quote, args.quote_kind, args.repeat_reason)
            elif args.command == 'transition':
                transition(data, args.job, args.state, args.evidence, args.task_id, args.artifact)
            elif args.command == 'bill':
                reconcile(data, args.job, args.amount, args.evidence)
            elif args.command == 'classify':
                classify(data, args.job, args.use, args.evidence)
            if args.command != 'report': save(args.journal, data)
            print(json.dumps(report(data), indent=2))
    except (ValueError, KeyError, OSError) as exc:
        p.exit(2, f'Journal rejected operation: {exc}\n')


if __name__ == '__main__':
    main()
