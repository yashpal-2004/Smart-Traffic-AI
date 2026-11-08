"""Semi-Markov Q-learning where each decision selects a green duration."""
from __future__ import annotations

from dataclasses import dataclass, field
import random

from app.agents.q_learning import QLearningAgent, State, observe
from app.simulator.environment import SignalConfig, TrafficEnvironment

DURATIONS = (10, 15, 20, 25, 30)


@dataclass
class DurationQLearningAgent(QLearningAgent):
    """Choose one target green duration per phase, then learn its interval return."""
    q_values: dict[State, list[float]] = field(default_factory=dict)

    def _values(self, state: State) -> list[float]:
        return self.q_values.setdefault(state, [0.0] * len(DURATIONS))

    @staticmethod
    def legal_actions(env: TrafficEnvironment) -> tuple[int, ...]:
        return tuple(i for i, duration in enumerate(DURATIONS)
                     if env.config.min_green <= duration <= env.config.max_green)


def train_duration_episode(env: TrafficEnvironment, agent: DurationQLearningAgent,
                           steps: int = 500) -> dict[str, float]:
    if steps < 1:
        raise ValueError("steps must be positive")
    total_reward = 0.0
    while env.time < steps:
        state = observe(env)
        served_before = env.metrics.total_served
        actions = agent.legal_actions(env)
        action = agent.act(env, explore=True)
        target = DURATIONS[action]
        interval_reward = 0.0
        elapsed = 0
        while env.time < steps and env.phase_elapsed < target:
            snap = env.step()
            interval_reward += -0.1 * sum(snap.queues.values())
            elapsed += 1
        # Amber is included in the duration decision's return and the next
        # phase starts with a fresh duration choice.
        if env.time < steps and not env.transitioning:
            env.request_switch()
            for _ in range(env.config.amber_seconds):
                if env.time >= steps:
                    break
                snap = env.step()
                interval_reward += -0.1 * sum(snap.queues.values())
                elapsed += 1
        interval_reward += 0.25 * (env.metrics.total_served - served_before)
        next_state = observe(env)
        next_actions = agent.legal_actions(env)
        discount = agent.discount ** max(1, elapsed)
        current = agent._values(state)
        future = max((agent._values(next_state)[a] for a in next_actions), default=0.0)
        current[action] += agent.learning_rate * (interval_reward + discount * future - current[action])
        total_reward += interval_reward
    agent.end_episode()
    return {"reward": total_reward, "served": float(env.metrics.total_served),
            "average_wait_seconds": env.metrics.average_wait_seconds,
            "max_queue": float(env.metrics.max_total_queue)}
