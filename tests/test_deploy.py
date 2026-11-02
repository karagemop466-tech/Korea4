import unittest
from unittest.mock import patch
from scripts.wait_for_legacy import latest_legacy, wait

SHA = 'abc'
def run(sha=SHA, status='completed', conclusion='success', created='2026-11-02T17:59:00Z', id=1):
    return {'event':'dynamic', 'name':'pages build and deployment', 'head_sha':sha,
            'status':status, 'conclusion':conclusion, 'created_at':created, 'id':id}

class DeploymentOrderTest(unittest.TestCase):
    def test_only_latest_legacy_run_for_the_same_commit_counts(self):
        older = run(id=1)
        newer = run(status='queued', conclusion=None, created='2026-11-02T18:00:00Z', id=2)
        wrong = run(sha='another', id=3)
        self.assertEqual(latest_legacy([older, newer, wrong], SHA), newer)
        self.assertIsNone(latest_legacy([wrong], SHA))

    @patch('scripts.wait_for_legacy.api')
    def test_successful_legacy_allows_custom_deploy(self, api):
        api.return_value = {'workflow_runs':[run()]}
        wait('owner/repo', SHA, attempts=1, interval=0)

    @patch('scripts.wait_for_legacy.api')
    def test_failed_legacy_stops_custom_deploy(self, api):
        api.return_value = {'workflow_runs':[run(conclusion='failure')]}
        with self.assertRaises(RuntimeError): wait('owner/repo', SHA, attempts=1, interval=0)

    @patch('scripts.wait_for_legacy.api')
    def test_switch_to_workflow_source_needs_no_legacy_run(self, api):
        api.side_effect = [{'workflow_runs':[]}, {'build_type':'workflow'}]
        wait('owner/repo', SHA, attempts=1, interval=0)

    @patch('scripts.wait_for_legacy.api')
    def test_missing_legacy_run_does_not_silently_race(self, api):
        api.side_effect = [{'workflow_runs':[]}, {'build_type':'legacy'}]
        with self.assertRaises(RuntimeError): wait('owner/repo', SHA, attempts=1, interval=0)
