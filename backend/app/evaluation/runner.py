"""Paired-seed evaluation for fixed-time and learned controllers."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from statistics import mean, median, pstdev

from app.agents.fixed_time import FixedTimeController
from app.agents.q_learning import QLearningAgent
from app.simulator.environment import Scenario, SignalConfig, TrafficEnvironment


@dataclass(frozen=True)
class EpisodeResult:
    controller: str
    scenario: str
    seed: int
    steps: int
    arrived: int
    served: int
    average_wait_seconds: float
    average_queue_length: float
    max_queue: int
    total_wait_seconds: int


def run_episode(controller: str, scenario: Scenario, seed: int, steps: int,
                config: SignalConfig, agent: QLearningAgent | None = None) -> EpisodeResult:
    env = TrafficEnvironment(scenario, seed=seed, config=config)
    fixed = FixedTimeController(green_seconds=max(config.min_green, min(20, config.max_green)), config=config)
    queue_sum = 0
    for _ in range(steps):
        if controller == "fixed_time":
            fixed.step(env)
        elif controller == "q_learning":
            if agent is None:
                raise ValueError("q_learning evaluation requires an agent")
            action = agent.act(env, explore=False)
            if action == 1:
                env.request_switch()
            env.step()
        else:
            raise ValueError(f"unknown controller: {controller}")
        queue_sum += sum(len(q) for q in env.queues.values())
    m = env.metrics
    return EpisodeResult(controller, scenario.name, seed, steps, m.total_arrived, m.total_served,
                         m.average_wait_seconds, queue_sum / steps, m.max_total_queue,
                         m.total_wait_seconds)


def summarize(results: list[EpisodeResult]) -> dict:
    grouped: dict[str, list[EpisodeResult]] = {}
    for result in results:
        grouped.setdefault(result.controller, []).append(result)
    summary = {}
    for controller, rows in grouped.items():
        waits = [r.average_wait_seconds for r in rows]
        queues = [r.average_queue_length for r in rows]
        served = [r.served for r in rows]
        summary[controller] = {
            "sample_count": len(rows),
            "average_wait_seconds": {"mean": mean(waits), "median": median(waits), "population_stddev": pstdev(waits)},
            "average_queue_length": {"mean": mean(queues), "median": median(queues), "population_stddev": pstdev(queues)},
            "vehicles_served": {"mean": mean(served), "median": median(served), "population_stddev": pstdev(served)},
        }
    return summary


def evaluate(scenarios: list[Scenario], seeds: list[int], steps: int, config: SignalConfig,
             agent: QLearningAgent) -> dict:
    if not scenarios or not seeds or steps < 1:
        raise ValueError("scenarios, seeds, and positive steps are required")
    results = []
    for scenario in scenarios:
        for seed in seeds:
            # Both policies receive identical exogenous arrival random streams.
            results.append(run_episode("fixed_time", scenario, seed, steps, config))
            results.append(run_episode("q_learning", scenario, seed, steps, config, agent))
    return {"protocol": {"paired_seeds": seeds, "steps_per_episode": steps,
                          "scenarios": [s.name for s in scenarios],
                          "wait_definition": "mean queueing seconds among vehicles served during the episode",
                          "queue_definition": "mean queued vehicles observed after each simulation step",
                          "training_data_excluded": True},
            "summary": summarize(results),
            "episodes": [asdict(row) for row in results]}


def write_report(report: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
