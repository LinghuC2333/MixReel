import copy
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/reference-replica-video/scripts'

def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + '.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

validator = load('validate_plan')
journal = load('job_journal')
redactor = load('redact_export')


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.p = json.loads((ROOT/'tests/fixtures/valid_plan.json').read_text())
    def test_valid_pending_plan_is_not_creative_approval(self):
        self.assertEqual(validator.validate(self.p), [])
        self.assertEqual(self.p['reviews']['storyboard'], 'pending')
    def test_gap(self):
        self.p['shots'][1]['start'] = 3.2
        self.assertTrue(any('gap' in x for x in validator.validate(self.p)))
    def test_music_coverage(self):
        self.p['music']['offset'] = 8
        self.assertTrue(any('excerpt' in x for x in validator.validate(self.p)))
    def test_count_unique_images_not_beats(self):
        self.p['illustration_count'] = 3
        self.assertTrue(any('unique images' in x for x in validator.validate(self.p)))
    def test_reused_keyframe_count(self):
        self.p['shots'][1]['keyframes'] = ['frame-1']; self.p['illustration_count'] = 1
        self.assertFalse(validator.validate(self.p))
    def test_unknown_reference(self):
        self.p['shots'][1]['bindings'] = ['missing']
        self.assertTrue(any('unknown reference' in x for x in validator.validate(self.p)))
    def test_duplicate_bindings(self):
        self.p['shots'][1]['bindings'] *= 2
        self.assertTrue(any('duplicate binding' in x for x in validator.validate(self.p)))
    def test_nan(self):
        self.p['duration'] = math.nan
        self.assertTrue(validator.validate(self.p))
    def test_bad_types_report_errors(self):
        for key in ('music','references','shots','reviews'):
            p = copy.deepcopy(self.p); p[key] = 42
            self.assertTrue(validator.validate(p))
        self.p['references'][0]['role'] = []
        self.assertTrue(validator.validate(self.p))
    def test_transition_consumes_handle(self):
        shot = self.p['shots'][1]
        shot['transition'] = {'type':'dissolve','duration':.5}
        shot['clip'] = {'asset':'clip.mp4','duration':3.4,'in':0,'speed':1}
        self.assertTrue(any('handle' in x for x in validator.validate(self.p)))
        shot['clip']['duration'] = 3.5
        self.assertFalse(validator.validate(self.p))
    def test_retime_checks_source_range(self):
        self.p['shots'][0]['clip'] = {'asset':'clip.mp4','duration':4,'in':1,'speed':1.2}
        self.assertTrue(any('range' in x for x in validator.validate(self.p)))
    def test_missing_scene(self):
        self.p['shots'][0]['description'] = ''
        self.assertTrue(any('description' in x for x in validator.validate(self.p)))


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.data = {'version':1,'budgets':{'USD':'1','EUR':'2'},'jobs':{}}
    def add(self, jid='job-1', request=None, **kw):
        values=dict(currency='USD',ceiling='.60',evidence='test-authority',quote='.50',quote_kind='quoted')
        values.update(kw)
        journal.reserve(self.data,jid,request or {'prompt':'synthetic'},'fixture-service','fixture-model','image',**values)
    def move(self, state):
        journal.transition(self.data,'job-1',state,'test-status',task_id='task-1' if state=='submitted' else None)
    def finish(self):
        self.move('submitting');self.move('submitted');self.move('generation_succeeded')
    def test_missing_quote_not_free(self):
        with self.assertRaises(ValueError): self.add(quote=None)
        self.add(quote=None,quote_kind='unavailable')
        self.assertEqual(journal.report(self.data)['totals']['USD']['remaining'],'0.40')
    def test_unknown_submission_cannot_repeat_even_with_override(self):
        self.add();self.move('submitting');self.move('outcome_unknown')
        with self.assertRaises(ValueError): self.add('job-2',repeat_reason='retry')
    def test_duplicate_request_blocked(self):
        self.add()
        with self.assertRaises(ValueError): self.add('job-2')
    def test_budget_counts_unreconciled_failure(self):
        self.add();self.move('submitting');self.move('failed')
        with self.assertRaises(ValueError): self.add('job-2',{'prompt':'different'})
    def test_billed_download_failure_still_counts(self):
        self.add();self.finish();journal.reconcile(self.data,'job-1','.50','invoice-test')
        self.assertEqual(journal.report(self.data)['totals']['USD']['billed'],'0.50')
        with self.assertRaises(ValueError):
            journal.transition(self.data,'job-1','downloaded','download-failed',artifact='/nonexistent/fixture.png')
        self.assertEqual(self.data['jobs']['job-1']['state'],'generation_succeeded')
    def test_success_cannot_be_resubmitted(self):
        self.add();self.finish()
        with self.assertRaises(ValueError): self.move('submitting')
    def test_task_id_immutable(self):
        self.add();self.move('submitting');self.move('submitted')
        with self.assertRaises(ValueError):
            journal.transition(self.data,'job-1','generation_succeeded','evidence',task_id='other')
    def test_cancel_before_submit_releases_budget(self):
        self.add();self.move('cancelled')
        self.assertEqual(journal.report(self.data)['totals']['USD']['remaining'],'1')
    def test_cannot_cancel_submitted_to_hide_charge(self):
        self.add();self.move('submitting')
        with self.assertRaises(ValueError): self.move('cancelled')
    def test_unknown_cost_cannot_be_billed_early(self):
        self.add();self.move('submitting')
        with self.assertRaises(ValueError): journal.reconcile(self.data,'job-1',0,'not-a-final-invoice')
    def test_actual_over_budget_remains_visible(self):
        self.add();self.finish();journal.reconcile(self.data,'job-1','1.25','invoice-test')
        self.assertEqual(journal.report(self.data)['totals']['USD']['remaining'],'-0.25')
    def test_currency_not_converted(self):
        self.add(currency='EUR')
        result=journal.report(self.data)['totals']
        self.assertEqual(result['USD']['remaining'],'1')
        self.assertEqual(result['EUR']['remaining'],'1.40')
    def test_nonfinite_rejected(self):
        for value in ('NaN','Infinity','-.1'):
            with self.assertRaises(ValueError): self.add(ceiling=value)
    def test_disposition_preserves_cost(self):
        self.add();self.finish();journal.reconcile(self.data,'job-1','.5','invoice-test')
        journal.classify(self.data,'job-1','discarded','visual defect')
        self.assertEqual(journal.report(self.data)['totals']['USD']['billed_by_use']['discarded'],'0.5')
    def test_cli_concurrent_budget_reservation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); jf=p/'journal.json'
            journal.save(jf, {'version':1,'budgets':{'USD':'1'},'jobs':{}})
            processes=[]
            for i in range(2):
                req=p/f'{i}.json';req.write_text(json.dumps({'prompt':str(i)}))
                args=[sys.executable,str(SCRIPTS/'job_journal.py'),'prepare',str(jf),'--job',f'job-{i}',
                      '--request',str(req),'--provider','fixture','--model','fixture','--operation','image',
                      '--currency','USD','--reserve','.6','--evidence','test-only']
                processes.append(subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE))
            statuses=[]
            for proc in processes:
                proc.communicate(timeout=10);statuses.append(proc.returncode)
            self.assertEqual(sorted(statuses),[0,2])
            self.assertEqual(len(json.loads(jf.read_text())['jobs']),1)


class RedactionTests(unittest.TestCase):
    def test_generic_token_fields(self):
        result=redactor.redact({'token':'fixture','sessionToken':'fixture','nested':{'refresh_token':'fixture'}})
        self.assertEqual(result['token'],'<REDACTED>')
        self.assertEqual(result['sessionToken'],'<REDACTED>')
        self.assertEqual(result['nested']['refresh_token'],'<REDACTED>')
    def test_nested_credentials_and_signed_links(self):
        source={'api_key':'fake-fixture','nested':[{'url':'https://example.invalid/a?X-Amz-Signature=fixture'}],
                'text':'request Bearer fake-fixture','ordinary':'https://example.invalid/docs?page=2'}
        result=redactor.redact(source)
        self.assertEqual(result['api_key'],'<REDACTED>')
        self.assertEqual(result['nested'][0]['url'],'<REDACTED>')
        self.assertNotIn('fake-fixture',result['text'])
        self.assertEqual(result['ordinary'],source['ordinary'])
        self.assertEqual(source['api_key'],'fake-fixture')
    def test_fragment_and_userinfo(self):
        for url in ('https://example.invalid/a#token=fixture','https://fake:fixture@example.invalid/a'):
            self.assertEqual(redactor.redact(url),'<REDACTED>')
    def test_source_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'in.json';path.write_text('{"token":"synthetic"}')
            r=subprocess.run([sys.executable,str(SCRIPTS/'redact_export.py'),str(path),str(path)],capture_output=True)
            self.assertNotEqual(r.returncode,0)
            self.assertEqual(path.read_text(),'{"token":"synthetic"}')


if __name__=='__main__': unittest.main()
