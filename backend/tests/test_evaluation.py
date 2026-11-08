import unittest

from app.agents.q_learning import QLearningAgent
from app.evaluation.runner import evaluate
from app.simulator.environment import BALANCED, NORTH_SURGE, SignalConfig


class EvaluationTests(unittest.TestCase):
    def test_matched_evaluation_is_reproducible_and_well_formed(self):
        a = evaluate([BALANCED, NORTH_SURGE], [17, 29], 80, SignalConfig(), QLearningAgent(epsilon=0, epsilon_min=0))
        b = evaluate([BALANCED, NORTH_SURGE], [17, 29], 80, SignalConfig(), QLearningAgent(epsilon=0, epsilon_min=0))
        self.assertEqual(a, b)
        self.assertEqual(len(a["episodes"]), 8)
        self.assertEqual(a["summary"]["fixed_time"]["sample_count"], 4)
        self.assertEqual(a["summary"]["q_learning"]["sample_count"], 4)
        self.assertEqual(a["protocol"]["paired_seeds"], [17, 29])
        self.assertIn("population_stddev", a["summary"]["q_learning"]["average_wait_seconds"])

    def test_invalid_evaluation_input_rejected(self):
        with self.assertRaises(ValueError):
            evaluate([], [1], 10, SignalConfig(), QLearningAgent())


if __name__ == "__main__":
    unittest.main()
