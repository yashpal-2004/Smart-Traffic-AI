"""Deterministic discrete four-way intersection simulator."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import random
from typing import Mapping


class Approach(str, Enum):
    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"


class Phase(str, Enum):
    NORTH_SOUTH = "north_south"
    EAST_WEST = "east_west"


@dataclass(frozen=True)
class Scenario:
    name: str
    arrival_rates: Mapping[Approach, float]

    def __post_init__(self):
        if set(self.arrival_rates) != set(Approach):
            raise ValueError("arrival_rates must define every approach")
        if any(not 0 <= x <= 1 for x in self.arrival_rates.values()):
            raise ValueError("arrival rates must be probabilities between 0 and 1")


BALANCED = Scenario("balanced", {a: .20 for a in Approach})
RUSH_HOUR = Scenario("rush_hour", {a: .40 for a in Approach})
NORTH_SURGE = Scenario("north_surge", {Approach.NORTH: .45, Approach.EAST: .15, Approach.SOUTH: .2, Approach.WEST: .15})
SCENARIOS = {s.name: s for s in (BALANCED, RUSH_HOUR, NORTH_SURGE)}


@dataclass(frozen=True)
class SignalConfig:
    min_green: int = 5
    max_green: int = 30
    amber_seconds: int = 2

    def __post_init__(self):
        if self.min_green < 1 or self.max_green < self.min_green:
            raise ValueError("green bounds must satisfy 1 <= min_green <= max_green")
        if self.amber_seconds < 1:
            raise ValueError("amber_seconds must be at least 1")


@dataclass
class Metrics:
    total_arrived: int = 0
    total_served: int = 0
    total_wait_seconds: int = 0
    max_total_queue: int = 0
    wait_by_vehicle: list[int] = field(default_factory=list)

    @property
    def average_wait_seconds(self) -> float:
        return sum(self.wait_by_vehicle) / len(self.wait_by_vehicle) if self.wait_by_vehicle else 0.0


@dataclass(frozen=True)
class Snapshot:
    time: int
    phase: Phase
    transitioning: bool
    phase_elapsed: int
    queues: Mapping[Approach, int]
    arrived: int
    served: int
    total_wait_seconds: int
    average_wait_seconds: float
    max_total_queue: int


class TrafficEnvironment:
    """One queued lane per approach; one car per green approach can clear per tick."""

    def __init__(self, scenario: Scenario = BALANCED, seed: int = 0,
                 config: SignalConfig = SignalConfig(), initial_phase: Phase = Phase.NORTH_SOUTH):
        self.scenario, self.seed, self.config = scenario, seed, config
        self._rng = random.Random(seed)
        self.phase = initial_phase
        self.phase_elapsed = self.time = 0
        self._amber_remaining = 0
        self._pending_phase: Phase | None = None
        self.queues: dict[Approach, list[int]] = {a: [] for a in Approach}
        self._arrival_times: dict[int, int] = {}
        self._next_id = 0
        self._last_served: list[int] = []
        self.metrics = Metrics()

    @property
    def transitioning(self) -> bool:
        return self._amber_remaining > 0

    @property
    def last_served(self) -> tuple[int, ...]:
        return tuple(self._last_served)

    def request_switch(self) -> bool:
        if self.transitioning or self.phase_elapsed < self.config.min_green:
            return False
        self._pending_phase = Phase.EAST_WEST if self.phase == Phase.NORTH_SOUTH else Phase.NORTH_SOUTH
        self._amber_remaining = self.config.amber_seconds
        return True

    def step(self, switch: bool = False) -> Snapshot:
        self._last_served = []
        if switch:
            self.request_switch()
        in_amber = self.transitioning

        for approach in Approach:
            if self._rng.random() < self.scenario.arrival_rates[approach]:
                self.queues[approach].append(self._next_id)
                self._arrival_times[self._next_id] = self.time
                self._next_id += 1
                self.metrics.total_arrived += 1

        if not in_amber:
            active = ((Approach.NORTH, Approach.SOUTH) if self.phase == Phase.NORTH_SOUTH
                      else (Approach.EAST, Approach.WEST))
            for approach in active:
                if self.queues[approach]:
                    vehicle_id = self.queues[approach].pop(0)
                    self._last_served.append(vehicle_id)
                    self.metrics.total_served += 1
                    self.metrics.wait_by_vehicle.append(self.time - self._arrival_times.pop(vehicle_id))

        self.metrics.total_wait_seconds += sum(len(q) for q in self.queues.values())
        self.metrics.max_total_queue = max(self.metrics.max_total_queue, sum(len(q) for q in self.queues.values()))
        self.time += 1
        if in_amber:
            self._amber_remaining -= 1
            if self._amber_remaining == 0:
                self.phase = self._pending_phase  # type: ignore[assignment]
                self._pending_phase = None
                self.phase_elapsed = 0
        else:
            self.phase_elapsed += 1
        return self.snapshot()

    def reset(self) -> Snapshot:
        return self.__init_and_snapshot()

    def __init_and_snapshot(self) -> Snapshot:
        scenario, seed, config, phase = self.scenario, self.seed, self.config, self.phase
        self.__init__(scenario, seed, config, phase)
        return self.snapshot()

    def snapshot(self) -> Snapshot:
        return Snapshot(self.time, self.phase, self.transitioning, self.phase_elapsed,
                        {a: len(q) for a, q in self.queues.items()}, self.metrics.total_arrived,
                        self.metrics.total_served, self.metrics.total_wait_seconds,
                        self.metrics.average_wait_seconds, self.metrics.max_total_queue)
