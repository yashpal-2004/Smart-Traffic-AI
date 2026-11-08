"""Optional integration checks for the SUMO/TraCI traffic model."""
from __future__ import annotations

import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app.agents.q_learning import QLearningAgent
from app.simulator.environment import Approach, BALANCED, Phase, Scenario, SignalConfig
from app.simulator.sumo.environment import SUMO_ENVIRONMENT_VERSION, SumoEnvironment, _binary


SUMO_AVAILABLE = bool(_binary("sumo") and _binary("netconvert"))
try:
    import traci  # noqa: F401
except ImportError:
    SUMO_AVAILABLE = False


@unittest.skipUnless(SUMO_AVAILABLE, "SUMO and TraCI are optional dependencies")
class SumoIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.env = SumoEnvironment(BALANCED, seed=42, config=SignalConfig(), steps=100)

    def tearDown(self):
        self.env.close()

    def test_signal_phases_only_green_opposing_approaches(self):
        states = self.env.visualization()["signal_states"]
        self.assertEqual({name for name, state in states.items() if state == "G"}, {"north", "south"})

        self.env.phase = Phase.EAST_WEST
        self.env._signal()
        states = self.env.visualization()["signal_states"]
        self.assertEqual({name for name, state in states.items() if state == "G"}, {"east", "west"})

    def test_switch_uses_amber_then_changes_opposing_pair(self):
        self.env.phase_elapsed = self.env.config.min_green
        self.assertTrue(self.env.request_switch())
        states = self.env.visualization()["signal_states"]
        self.assertEqual({name for name, state in states.items() if state == "y"}, {"north", "south"})

        self.env.step()
        self.env.step()
        self.assertEqual(self.env.phase, Phase.EAST_WEST)
        states = self.env.visualization()["signal_states"]
        self.assertEqual({name for name, state in states.items() if state == "G"}, {"east", "west"})

    def test_visualization_exposes_network_junction_and_live_positions(self):
        for _ in range(30):
            self.env.step()
        view = self.env.visualization()
        self.assertEqual(view["network_bounds"], {"min_x": 0.0, "max_x": 600.0,
                                                   "min_y": 0.0, "max_y": 600.0})
        junction = view["junction_bounds"]
        self.assertLess(junction["min_x"], junction["max_x"])
        self.assertLess(junction["min_y"], junction["max_y"])
        self.assertTrue(view["vehicles"])
        for vehicle in view["vehicles"]:
            self.assertGreaterEqual(vehicle["x"], 0)
            self.assertLessEqual(vehicle["x"], 600)
            self.assertGreaterEqual(vehicle["y"], 0)
            self.assertLessEqual(vehicle["y"], 600)

    def test_snapshot_queues_match_sumo_halting_counts(self):
        for _ in range(50):
            self.env.step()
        snapshot = self.env.snapshot()
        lane_by_approach = {
            "north": "north_in_0", "east": "east_in_0",
            "south": "south_in_0", "west": "west_in_0",
        }
        pending = self.env.conn.simulation.getPendingVehicles()
        for approach, lane in lane_by_approach.items():
            pending_count = sum(vehicle_id.startswith(f"flow_{approach}.") for vehicle_id in pending)
            self.assertEqual(snapshot.queues[Approach(approach)],
                             self.env.conn.lane.getLastStepHaltingNumber(lane) + pending_count)

    def test_pending_departures_are_counted_in_the_approach_queue(self):
        self.env.close()
        self.env = SumoEnvironment(Scenario("saturated", {approach: .8 for approach in Approach}),
                                   seed=7, config=SignalConfig(), steps=200)
        for _ in range(150):
            self.env.step()
        pending = self.env.conn.simulation.getPendingVehicles()
        self.assertTrue(pending, "saturated demand should produce delayed departures")
        snapshot = self.env.snapshot()
        pending_by_approach = {
            approach: sum(vehicle_id.startswith(f"flow_{approach.value}.") for vehicle_id in pending)
            for approach in Approach
        }
        halting = {
            Approach.NORTH: self.env.conn.lane.getLastStepHaltingNumber("north_in_0"),
            Approach.EAST: self.env.conn.lane.getLastStepHaltingNumber("east_in_0"),
            Approach.SOUTH: self.env.conn.lane.getLastStepHaltingNumber("south_in_0"),
            Approach.WEST: self.env.conn.lane.getLastStepHaltingNumber("west_in_0"),
        }
        for approach in Approach:
            self.assertEqual(snapshot.queues[approach], halting[approach] + pending_by_approach[approach])


class SumoCheckpointTests(unittest.TestCase):
    def test_checkpoint_must_match_environment_version(self):
        from app.api import routes

        previous_agent = routes.sumo_agent
        try:
            with TemporaryDirectory() as directory:
                path = Path(directory) / "sumo_q_table.json"
                with patch.object(routes, "SUMO_MODEL_PATH", path):
                    QLearningAgent().save(path)
                    self.assertIsNone(routes.load_sumo_agent())

                    data = json.loads(path.read_text(encoding="utf-8"))
                    data["sumo_environment_version"] = SUMO_ENVIRONMENT_VERSION
                    path.write_text(json.dumps(data), encoding="utf-8")
                    self.assertIsInstance(routes.load_sumo_agent(), QLearningAgent)
        finally:
            routes.sumo_agent = previous_agent


if __name__ == "__main__":
    unittest.main()
