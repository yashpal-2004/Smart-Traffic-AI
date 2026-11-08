"""Train on separate seeds, evaluate on held-out seeds, and save JSON results."""
import argparse
import random

from app.agents.q_learning import QLearningAgent, train_episode
from app.evaluation.runner import evaluate, write_report
from app.simulator.environment import SCENARIOS, SignalConfig, TrafficEnvironment


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=300)
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--output", default="artifacts/evaluation.json")
    args = parser.parse_args()
    if args.episodes < 1 or args.steps < 1:
        parser.error("episodes and steps must be positive")

    agent = QLearningAgent()
    training_rng = random.Random(2026)
    scenarios = list(SCENARIOS.values())
    for _ in range(args.episodes):
        scenario = scenarios[training_rng.randrange(len(scenarios))]
        seed = training_rng.randrange(1_000_000)
        agent._rng.seed(training_rng.randrange(1_000_000))
        train_episode(TrafficEnvironment(scenario, seed=seed), agent, args.steps)

    report = evaluate(scenarios, [101, 202, 303, 404, 505], args.steps,
                      SignalConfig(), agent)
    write_report(report, args.output)
    agent.save("backend/artifacts/q_table.json")
    print(f"Wrote evaluation report to {args.output}")
    for name, metrics in report["summary"].items():
        print(f"{name}: wait={metrics['average_wait_seconds']['mean']:.2f}s, "
              f"queue={metrics['average_queue_length']['mean']:.2f}, "
              f"served={metrics['vehicles_served']['mean']:.1f} (n={metrics['sample_count']})")


if __name__ == "__main__":
    main()
