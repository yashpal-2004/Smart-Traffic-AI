import tempfile
import unittest
from pathlib import Path

from app.agents.q_learning import QLearningAgent, observe, train_episode
from app.simulator.environment import SignalConfig, TrafficEnvironment


class QLearningTests(unittest.TestCase):
    def test_observation_is_bounded_and_phase_aware(self):
        env = TrafficEnvironment(seed=4)
        state = observe(env)
        self.assertEqual(len(state), 6)
        self.assertTrue(all(0 <= n <= 5 for n in state[:4]))

    def test_actions_respect_minimum_and_maximum_green(self):
        env = TrafficEnvironment(config=SignalConfig(2, 4, 1))
        agent = QLearningAgent(epsilon=0)
        self.assertEqual(agent.legal_actions(env), (0,))
        for _ in range(2): env.step()
        self.assertEqual(agent.legal_actions(env), (0, 1))
        for _ in range(2): env.step()
        self.assertEqual(agent.legal_actions(env), (1,))

    def test_training_reproducible_for_same_seed(self):
        outputs = []
        for _ in range(2):
            agent = QLearningAgent()
            agent._rng.seed(12)
            env = TrafficEnvironment(seed=9)
            outputs.append((train_episode(env, agent, 80), agent.q_values))
        self.assertEqual(outputs[0], outputs[1])

    def test_checkpoint_round_trip(self):
        agent = QLearningAgent(epsilon=.4)
        agent.q_values[(1, 2, 3, 4, 0, 1)] = [1.5, -2.0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "q.json"
            agent.save(path)
            restored = QLearningAgent.load(path)
        self.assertEqual(restored.epsilon, .4)
        self.assertEqual(restored.q_values, agent.q_values)


if __name__ == "__main__":
    unittest.main()
