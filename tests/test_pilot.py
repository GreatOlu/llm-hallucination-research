import copy
import json
from pathlib import Path
import tempfile
import unittest
from src.experiments.run_pilot import prepare, run, save, locked


class Retriever:
    def __init__(self):
        self.calls = 0

    def retrieve(self, question, top_k):
        assert top_k == 5
        self.calls += 1
        return [{'document_id': f'doc_{i}', 'context': f'Passage {i}'} for i in range(5)]


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'pilot.json'
        self.retriever = Retriever()
        self.state = prepare({'questions': [{'id': str(i), 'question': 'Question?',
            'group': 'answerable', 'reference_answers': ['Answer']} for i in range(5)]}, self.retriever, 'fake-model')

    def good(self, prompt):
        # Request intent is already on disk before generation.
        assert any(r['status'] == 'in_flight' for r in json.loads(self.path.read_text())['records'])
        return {'answer': 'Answer', 'input_tokens': 10, 'output_tokens': 2}

    def test_resume_and_shared_evidence(self):
        self.assertEqual(self.retriever.calls, 5)
        for offset in range(0, 20, 4):
            rows = self.state['records'][offset:offset+4]
            self.assertEqual(rows[0]['retrieved_document_ids'], [])
            self.assertEqual(rows[2]['retrieved_passages'], rows[3]['retrieved_passages'])
        self.assertEqual(run(self.state, self.path, self.good, 2), 2)
        resumed = json.loads(self.path.read_text())
        self.assertEqual(run(resumed, self.path, self.good, 20), 18)
        self.assertEqual(run(resumed, self.path, self.good, 20), 0)
        self.assertTrue(all(r['status'] == 'completed' for r in resumed['records']))

    def test_failure_stops_and_sanitizes(self):
        def fail(prompt):
            raise RuntimeError('SECRET must not be saved')
        self.assertEqual(run(self.state, self.path, fail, 20), 1)
        self.assertNotIn('SECRET', self.path.read_text())
        self.assertEqual(self.state['records'][0]['status'], 'error')
        self.assertEqual(run(self.state, self.path, self.good, 1), 1)
        self.assertEqual(self.state['records'][0]['status'], 'error')

    def test_crash_not_retried(self):
        def crash(prompt):
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            run(self.state, self.path, crash, 20)
        resumed = json.loads(self.path.read_text())
        self.assertEqual(resumed['records'][0]['status'], 'in_flight')
        self.assertEqual(run(resumed, self.path, self.good, 20), 19)

    def test_empty_response_records_usage_and_stops(self):
        self.assertEqual(run(self.state, self.path, lambda p: {
            'answer': '', 'input_tokens': 10, 'output_tokens': 200}, 20), 1)
        self.assertEqual(self.state['records'][0]['status'], 'empty_response')
        self.assertEqual(self.state['records'][0]['output_tokens'], 200)

    def test_incomplete_text_stops(self):
        self.assertEqual(run(self.state, self.path, lambda p: {
            'answer': 'Partial answer', 'input_tokens': 10, 'output_tokens': 1000,
            'response_status': 'incomplete', 'incomplete_reason': 'max_output_tokens',
            'reasoning_tokens': 950}, 20), 1)
        row = self.state['records'][0]
        self.assertEqual(row['status'], 'incomplete')
        self.assertEqual(row['reasoning_tokens'], 950)
        self.assertEqual(row['incomplete_reason'], 'max_output_tokens')

    def test_lock_excludes_second_runner(self):
        with locked(self.path):
            with self.assertRaises(ValueError):
                with locked(self.path):
                    pass


if __name__ == '__main__':
    unittest.main()
