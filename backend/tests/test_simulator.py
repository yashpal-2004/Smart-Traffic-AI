import unittest

from app.simulator.environment import (
    Approach, Phase, Scenario, SignalConfig, TrafficEnvironment,
)
from app.agents.fixed_time import FixedTimeController


class SimulatorTests(unittest.TestCase):
    def test_seed_reproduces_entire_trace(self):
        scenario = Scenario("test", {a: 0.4 for a in Approach})
        a = TrafficEnvironment(scenario, seed=42)
        b = TrafficEnvironment(scenario, seed=42)
        self.assertEqual([a.step() for _ in range(50)], [b.step() for _ in range(50)])

    def test_no_service_during_transition_and_switch_is_min_green_gated(self):
        scenario = Scenario("north", {a: (1 if a == Approach.EAST else 0) for a in Approach})
        env = TrafficEnvironment(scenario, seed=0, config=SignalConfig(2, 10, 2))
        env.step(); env.step()
        self.assertTrue(env.request_switch())
        first = env.step()
        self.assertTrue(first.transitioning)
        self.assertEqual(env.metrics.total_served, 0)
        second = env.step()
        self.assertFalse(second.transitioning)
        self.assertEqual(second.phase, Phase.EAST_WEST)
        self.assertEqual(env.metrics.total_served, 0)
        env.step()
        self.assertEqual(env.metrics.total_served, 1)

    def test_wait_time_and_queue_metrics_hand_calculated(self):
        scenario = Scenario("north", {a: (1 if a == Approach.EAST else 0) for a in Approach})
        env = TrafficEnvironment(scenario, seed=1, config=SignalConfig(3, 20, 2))
        # East arrivals queue while north-south is green.
        env.step(); env.step(); env.step()
        self.assertEqual(env.metrics.total_arrived, 3)
        self.assertEqual(env.metrics.total_served, 0)
        self.assertEqual(env.metrics.total_wait_seconds, 1 + 2 + 3)
        self.assertEqual(env.metrics.max_total_queue, 3)
        env.request_switch(); env.step(); env.step(); env.step()
        self.assertEqual(env.metrics.total_served, 1)
        self.assertEqual(env.metrics.wait_by_vehicle, [5])

    def test_fixed_time_controller_switches_after_green_duration(self):
        env = TrafficEnvironment(seed=0, config=SignalConfig(2, 10, 1))
        policy = FixedTimeController(3, env.config)
        for _ in range(3):
            policy.step(env)
        self.assertEqual(env.phase, Phase.NORTH_SOUTH)
        policy.step(env)
        self.assertEqual(env.phase, Phase.EAST_WEST)

    def test_invalid_configuration_rejected(self):
        with self.assertRaises(ValueError):
            SignalConfig(0, 5, 2)
        with self.assertRaises(ValueError):
            Scenario("bad", {a: 2 for a in Approach})


if __name__ == "__main__":
    unittest.main()
