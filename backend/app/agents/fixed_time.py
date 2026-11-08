"""Deterministic fixed-time baseline policy."""
from dataclasses import dataclass

from app.simulator.environment import Phase, SignalConfig, TrafficEnvironment


@dataclass
class FixedTimeController:
    green_seconds: int = 20
    config: SignalConfig = SignalConfig()

    def __post_init__(self) -> None:
        if not self.config.min_green <= self.green_seconds <= self.config.max_green:
            raise ValueError("green_seconds must be within configured green bounds")

    def act(self, env: TrafficEnvironment) -> bool:
        """Return whether the policy requested a switch this tick."""
        return (not env.transitioning
                and env.phase_elapsed >= self.green_seconds
                and ((env.phase == Phase.NORTH_SOUTH) or (env.phase == Phase.EAST_WEST)))

    def step(self, env: TrafficEnvironment):
        return env.step(switch=self.act(env))
