"""Controlled duration-action experiment against fixed-time and hold/switch Q-learning."""
from app.agents.duration_q_learning import DurationQLearningAgent, train_duration_episode
from app.agents.q_learning import QLearningAgent, train_episode
from app.evaluation.runner import evaluate, write_report
from app.simulator.environment import SCENARIOS, SignalConfig, TrafficEnvironment
import random


def main():
    episodes, steps = 1500, 500
    scenarios = list(SCENARIOS.values())
    rng = random.Random(2027)
    duration = DurationQLearningAgent()
    hold_switch = QLearningAgent()
    for _ in range(episodes):
        scenario = scenarios[rng.randrange(len(scenarios))]
        seed = rng.randrange(1_000_000)
        duration._rng.seed(rng.randrange(1_000_000))
        train_duration_episode(TrafficEnvironment(scenario, seed), duration, steps)
        hold_switch._rng.seed(rng.randrange(1_000_000))
        train_episode(TrafficEnvironment(scenario, seed), hold_switch, steps)
    report = evaluate(scenarios, [711, 822, 933, 1044, 1155], steps,
                      SignalConfig(), hold_switch, duration)
    write_report(report, "artifacts/duration-action-evaluation.json")
    for name, values in report["summary"].items():
        print(f"{name}: wait={values['average_wait_seconds']['mean']:.2f}s "
              f"queue={values['average_queue_length']['mean']:.2f} "
              f"served={values['vehicles_served']['mean']:.1f}")


if __name__ == "__main__":
    main()
