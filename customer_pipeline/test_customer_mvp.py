"""Changed-connection controls only. No real customer/model PASS assertion."""
import copy
import io
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch
import customer_mvp as mvp
import customer_model_adapter as adapter
import customer_release_gate as gate


def context_control():
    context = {key: 'CONTROL_SOURCE' for key in ('central_master', 'copy_rules', 'master',
                'checkpoint', 'central_checkpoint', 'customers', 'tool42_master', 'tool42_checkpoint')}
    context['feedback'] = json.dumps({'current_feedback_ref': 'CONTROL_REF', 'cases': []})
    context['release_gate'] = Path(gate.__file__).read_text(encoding='utf-8')
    context['source_sha256'] = {key: gate.digest(value) for key, value in context.items()}
    return context


class ControlledModel:
    def __init__(self, decisions):
        self.decisions = list(decisions)
        self.calls = []

    def generate(self, packet, previous=None, review=None):
        self.calls.append(('rewrite' if previous is not None else 'generate', copy.deepcopy(packet)))
        return ('CONTROL_PRIVATE_B' if previous is not None else 'CONTROL_PRIVATE_A'), 'control-generation'

    def review(self, packet, draft):
        self.calls.append(('review', copy.deepcopy(packet)))
        verdict = self.decisions.pop(0)
        return {'checks': {key: {'verdict': verdict, 'reason': 'CONTROL_REASON',
                                 'evidence_refs': ['customer']} for key in gate.CATEGORIES}}, 'control-review'


class ControlledRuntime:
    def __init__(self, decisions=('PASS',), save='PASS', unchanged=True):
        self.model = ControlledModel(decisions)
        self.receipts = []
        self.save = save
        self.is_unchanged = unchanged
        self.events = []

    def load(self):
        self.events.append('load')
        return context_control()

    def customer(self, request, context):
        self.events.append('customer')
        return {'id': 'CONTROL_NOT_CUSTOMER'}, [{'고유번호': 'CONTROL_NOT_CUSTOMER'}]

    def unchanged(self, context):
        self.events.append('freshness')
        return self.is_unchanged

    def persist(self, receipt):
        self.events.append('save')
        self.receipts.append(copy.deepcopy(receipt))
        return {'status': self.save, 'receipt_id': 'control-receipt'}


REQUEST = {'tool': 'TOOL042', 'customer_id': 'CONTROL_NOT_CUSTOMER',
           'task': 'CONTROL_REQUEST', 'mode': 'history_question'}


class DedicatedEntryTests(unittest.TestCase):
    def assert_hidden(self, result):
        self.assertEqual(result['status'], 'HOLD')
        self.assertFalse(result['output_allowed'])
        self.assertNotIn('CONTROL_PRIVATE', json.dumps(result))
        self.assertEqual(result['rows'], [])

    def test_pass_only_after_review_freshness_and_save(self):
        rt = ControlledRuntime()
        result = mvp.execute(REQUEST, rt)
        self.assertTrue(result['output_allowed'])
        self.assertEqual(result['stages'][-2:], ['CENTRAL_SAVED', 'PASS_OUTPUT'])
        self.assertEqual(rt.events, ['load', 'customer', 'freshness', 'save'])
        self.assertNotIn('CONTROL_PRIVATE', json.dumps(rt.receipts))

    def test_one_semantic_rewrite_then_recheck(self):
        rt = ControlledRuntime(('FAIL', 'PASS'))
        result = mvp.execute(REQUEST, rt)
        self.assertEqual(result['rewrite_count'], 1)
        self.assertEqual(result['body'], 'CONTROL_PRIVATE_B')
        self.assertEqual([item[0] for item in rt.model.calls], ['generate', 'review', 'rewrite', 'review'])
        self.assertEqual(rt.model.calls[0][1], rt.model.calls[-1][1])

    def test_two_semantic_failures_never_release(self):
        rt = ControlledRuntime(('FAIL', 'FAIL'))
        result = mvp.execute(REQUEST, rt)
        self.assert_hidden(result)
        self.assertEqual(result['rewrite_count'], 1)
        self.assertEqual(len(rt.model.calls), 4)

    def test_review_hold_gets_one_rewrite_then_hold(self):
        rt = ControlledRuntime(('HOLD', 'HOLD'))
        result = mvp.execute(REQUEST, rt)
        self.assert_hidden(result)
        self.assertEqual(result['rewrite_count'], 1)

    def test_storage_failure_no_body_no_second_write(self):
        rt = ControlledRuntime(save='HOLD')
        self.assert_hidden(mvp.execute(REQUEST, rt))
        self.assertEqual(len(rt.receipts), 1)

    def test_source_changed_after_generation_no_body(self):
        rt = ControlledRuntime(unchanged=False)
        self.assert_hidden(mvp.execute(REQUEST, rt))

    def test_caller_cannot_supply_semantic_pass(self):
        rt = ControlledRuntime()
        self.assert_hidden(mvp.execute({**REQUEST, 'review': 'PASS'}, rt))
        self.assertEqual(rt.model.calls, [])

    def test_material_scope_stops_before_model(self):
        rt = ControlledRuntime()
        result = mvp.execute({**REQUEST, 'mode': 'sales_material'}, rt)
        self.assert_hidden(result)
        self.assertEqual(result['reason'], 'ACTUAL_MATERIALS_EVIDENCE_REQUIRED')
        self.assertEqual(rt.model.calls, [])

    def test_missing_customer_stops_before_model(self):
        rt = ControlledRuntime()
        def missing(*args):
            raise mvp.Hold('CUSTOMER_EVIDENCE_REQUIRED')
        rt.customer = missing
        self.assert_hidden(mvp.execute(REQUEST, rt))
        self.assertEqual(rt.model.calls, [])

    def test_incomplete_review_is_not_pass(self):
        with self.assertRaises(mvp.Hold):
            mvp.validate_review({'checks': {}}, {'rules': {}})

    def test_response_adapter_no_stream_and_no_store(self):
        captured = []
        def transport(req, **kwargs):
            captured.append(json.loads(req.data))
            return io.StringIO(json.dumps({'status': 'completed', 'id': 'control-response',
                'output': [{'type': 'message', 'content': [{'type': 'output_text',
                           'text': json.dumps({'body': 'CONTROL_PRIVATE'})}]}]}))
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'CONTROL_FAKE_KEY', 'WIC_MODEL': 'CONTROL_MODEL'}):
            with patch.object(adapter, 'urlopen', transport):
                adapter.ResponsesModel().generate({'rules': {}, 'customer': {}})
        self.assertFalse(captured[0]['stream'])
        self.assertFalse(captured[0]['store'])
        self.assertEqual(captured[0]['text']['format']['type'], 'json_schema')


if __name__ == '__main__':
    unittest.main(verbosity=2)
