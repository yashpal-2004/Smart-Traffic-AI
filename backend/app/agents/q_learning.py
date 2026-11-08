"""Tabular Q-learning for discrete traffic-signal control."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import random

from app.simulator.environment import Approach, Phase, TrafficEnvironment

Action = int  # 0 = hold; 1 = request phase switch
State = tuple[int, int, int, int, int, int]


def observe(env: TrafficEnvironment) -> State:
    """Bucket queue lengths and green age into a compact tabular state."""
    queues = tuple(min(5, len(env.queues[a])) for a in Approach)
    phase_bit = 0 if env.phase == Phase.NORTH_SOUTH else 1
    green_age = min(3, env.phase_elapsed // max(1, env.config.min_green))
    return (*queues, phase_bit, green_age)


@dataclass
class QLearningAgent:
    learning_rate: float = 0.15
    discount: float = 0.95
    epsilon: float = 1.0
    epsilon_min: float = 0.0
    epsilon_decay: float = 0.98
    q_values: dict[State, list[float]] = field(default_factory=dict)
    _rng: random.Random = field(default_factory=lambda: random.Random(0), repr=False)

    def __post_init__(self):
        if not 0 < self.learning_rate <= 1 or not 0 <= self.discount <= 1:
            raise ValueError("learning_rate must be (0,1] and discount must be [0,1]")
        if not 0 <= self.epsilon_min <= self.epsilon <= 1 or not 0 < self.epsilon_decay <= 1:
            raise ValueError("invalid epsilon schedule")

    def _values(self, state: State) -> list[float]:
        return self.q_values.setdefault(state, [0.0, 0.0])

    @staticmethod
    def legal_actions(env: TrafficEnvironment) -> tuple[Action, ...]:
        if env.transitioning:
            return (0,)
        if env.phase_elapsed < env.config.min_green:
            return (0,)
        if env.phase_elapsed >= env.config.max_green:
            return (1,)
        return (0, 1)

    def act(self, env: TrafficEnvironment, explore: bool = False) -> Action:
        state = observe(env)
        actions = self.legal_actions(env)
        if explore and self._rng.random() < self.epsilon:
            return self._rng.choice(actions)
        values = self._values(state)
        return max(actions, key=lambda action: values[action])

    def update(self, state: State, action: Action, reward: float, next_state: State,
               next_actions: tuple[Action, ...]) -> None:
        current = self._values(state)
        future = max((self._values(next_state)[a] for a in next_actions), default=0.0)
        current[action] += self.learning_rate * (reward + self.discount * future - current[action])

    def end_episode(self) -> None:
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {"version": 1, "epsilon": self.epsilon,
                "q_values": {",".join(map(str, state)): values for state, values in self.q_values.items()}}
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "QLearningAgent":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("version") != 1:
            raise ValueError("unsupported Q-table checkpoint version")
        agent = cls(epsilon=float(data["epsilon"]))
        agent.q_values = {tuple(map(int, key.split(","))): list(map(float, values))
                          for key, values in data["q_values"].items()}
        return agent


def train_episode(env: TrafficEnvironment, agent: QLearningAgent, steps: int = 500) -> dict[str, float]:
    """Train one fixed-length episode; reward favors serving cars and short queues."""
    if steps < 1:
        raise ValueError("steps must be positive")
    total_reward = 0.0
    for _ in range(steps):
        state = observe(env)
        action = agent.act(env, explore=True)
        if action == 1 and not env.request_switch():
            action = 0
        before_served = env.metrics.total_served
        snapshot = env.step()
        reward = float(env.metrics.total_served - before_served) - 0.1 * sum(snapshot.queues.values())
        next_state = observe(env)
        agent.update(state, action, reward, next_state, agent.legal_actions(env))
        total_reward += reward
    agent.end_episode()
    return {"reward": total_reward, "served": float(env.metrics.total_served),
            "average_wait_seconds": env.metrics.average_wait_seconds,
            "max_queue": float(env.metrics.max_total_queue)}
