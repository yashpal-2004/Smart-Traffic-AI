import unittest
import time
from fastapi.testclient import TestClient

from app.api.routes import app, runs


class ApiTests(unittest.TestCase):
    def setUp(self):
        runs.clear()
        self.client = TestClient(app)

    def test_health_and_scenarios(self):
        self.assertEqual(self.client.get('/api/health').json()['status'], 'ok')
        self.assertEqual(len(self.client.get('/api/scenarios').json()), 3)

    def test_run_lifecycle(self):
        created = self.client.post('/api/runs', json={'seed': 9}).json()
        run_id = created['id']
        self.assertTrue(created['paused'])
        stepped = self.client.post(f'/api/runs/{run_id}/step', json={'steps': 5}).json()
        self.assertEqual(stepped['time'], 5)
        resumed = self.client.post(f'/api/runs/{run_id}/control/resume').json()
        self.assertFalse(resumed['paused'])
        reset = self.client.post(f'/api/runs/{run_id}/control/reset').json()
        self.assertEqual(reset['time'], 0)

    def test_invalid_inputs_and_unknown_run(self):
        self.assertEqual(self.client.post('/api/runs', json={'scenario': 'unknown'}).status_code, 422)
        self.assertEqual(self.client.get('/api/runs/missing').status_code, 404)

    def test_small_evaluation(self):
        response = self.client.post('/api/evaluations', json={'scenarios':['balanced'], 'seeds':[2], 'steps':20})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['summary']['fixed_time']['sample_count'], 1)

    def test_run_history_and_training_route(self):
        created = self.client.post('/api/runs', json={}).json()
        run_id = created['id']
        stepped = self.client.post(f'/api/runs/{run_id}/step', json={'steps': 4}).json()
        self.assertEqual(len(stepped['history']), 4)
        self.assertEqual(stepped['history'][-1]['time'], 4)
        result = self.client.post('/api/training', json={'episodes': 1, 'steps': 50})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()['status'], 'queued')
        for _ in range(100):
            status = self.client.get('/api/training').json()
            if status['status'] in {'complete', 'failed'}:
                break
            time.sleep(.01)
        self.assertEqual(status['status'], 'complete')
        self.assertGreater(status['states'], 0)


if __name__ == '__main__':
    unittest.main()
