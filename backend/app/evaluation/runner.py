"""Paired-seed evaluation for fixed-time and learned controllers."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from statistics import mean, median, pstdev, stdev

from app.agents.fixed_time import FixedTimeController
from app.agents.q_learning import QLearningAgent
from app.agents.duration_q_learning import DurationQLearningAgent, DURATIONS
from app.simulator.environment import Scenario, SignalConfig, TrafficEnvironment


def paired_delta_summary(deltas: list[dict]) -> dict:
    """Summarize paired differences with a two-sided 95% t interval."""
    t_critical = (None, 12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306,
                  2.262, 2.228, 2.201, 2.179, 2.160, 2.145, 2.131, 2.120, 2.110,
                  2.101, 2.093, 2.086, 2.080, 2.074, 2.069, 2.064, 2.060, 2.056,
                  2.052, 2.048, 2.045, 2.042)
    summary = {}
    for controller in ("q_learning", "duration_q_learning"):
        rows = [row for row in deltas if row["controller"] == controller]
        if not rows:
            continue
        metrics = {}
        for key in ("wait_seconds", "queue_length", "vehicles_served"):
            values = [row[key] for row in rows]
            avg = mean(values)
            if len(values) < 2:
                low = high = None
            else:
                critical = t_critical[len(values) - 1] if len(values) <= 30 else 1.96
                margin = critical * stdev(values) / len(values) ** 0.5
                low, high = avg - margin, avg + margin
            metrics[key] = {"mean": round(avg, 3),
                            "ci95_low": round(low, 3) if low is not None else None,
                            "ci95_high": round(high, 3) if high is not None else None}
        wait_values = [row["wait_seconds"] for row in rows]
        metrics["wait_improvements"] = sum(value < 0 for value in wait_values)
        metrics["wait_ties"] = sum(value == 0 for value in wait_values)
        metrics["sample_count"] = len(rows)
        summary[controller] = metrics
    return summary


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
        elif controller == "duration_q_learning":
            if not isinstance(agent, DurationQLearningAgent):
                raise ValueError("duration_q_learning requires a duration agent")
            action = agent.act(env, explore=False)
            target = DURATIONS[action]
            while env.time < steps and env.phase_elapsed < target:
                env.step()
                queue_sum += sum(len(q) for q in env.queues.values())
            if env.time < steps and not env.transitioning:
                env.request_switch()
                for _ in range(config.amber_seconds):
                    if env.time >= steps: break
                    env.step()
                    queue_sum += sum(len(q) for q in env.queues.values())
            continue
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
             agent: QLearningAgent, duration_agent: DurationQLearningAgent | None = None) -> dict:
    if not scenarios or not seeds or steps < 1:
        raise ValueError("scenarios, seeds, and positive steps are required")
    results = []
    for scenario in scenarios:
        for seed in seeds:
            # Both policies receive identical exogenous arrival random streams.
            results.append(run_episode("fixed_time", scenario, seed, steps, config))
            results.append(run_episode("q_learning", scenario, seed, steps, config, agent))
            if duration_agent is not None:
                results.append(run_episode("duration_q_learning", scenario, seed, steps, config, duration_agent))
    by_key = {(row.scenario, row.seed, row.controller): row for row in results}
    paired_deltas = []
    for scenario in scenarios:
        for seed in seeds:
            baseline = by_key[(scenario.name, seed, "fixed_time")]
            for controller in ("q_learning", "duration_q_learning"):
                candidate = by_key.get((scenario.name, seed, controller))
                if candidate is None:
                    continue
                paired_deltas.append({
                    "scenario": scenario.name,
                    "seed": seed,
                    "controller": controller,
                    "wait_seconds": round(candidate.average_wait_seconds - baseline.average_wait_seconds, 3),
                    "queue_length": round(candidate.average_queue_length - baseline.average_queue_length, 3),
                    "vehicles_served": candidate.served - baseline.served,
                })
    scenario_summaries = {
        scenario.name: paired_delta_summary([row for row in paired_deltas if row["scenario"] == scenario.name])
        for scenario in scenarios
    }
    return {"protocol": {"paired_seeds": seeds, "steps_per_episode": steps,
                          "scenarios": [s.name for s in scenarios],
                          "wait_definition": "mean queueing seconds among vehicles served during the episode",
                          "queue_definition": "mean queued vehicles observed after each simulation step",
                          "paired_interval_method": "Two-sided 95% Student t interval on paired differences; t critical values for up to 30 observations, z=1.96 approximation above 30; unavailable with one observation",
                          "paired_interval_assumptions": "Paired differences are independent and their mean is approximately normal; pooled interval combines selected scenarios",
                          "training_data_excluded": True,
                          "duration_actions_seconds": list(DURATIONS) if duration_agent is not None else None},
            "summary": summarize(results),
            "paired_deltas_vs_fixed_time": paired_deltas,
            "paired_summary_vs_fixed_time": paired_delta_summary(paired_deltas),
            "paired_summary_by_scenario": scenario_summaries,
            "episodes": [asdict(row) for row in results]}


def write_report(report: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
