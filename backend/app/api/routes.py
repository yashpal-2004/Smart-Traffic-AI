"""Validated API models, in-memory run manager, and routes."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.agents.fixed_time import FixedTimeController
from app.agents.q_learning import QLearningAgent
from app.evaluation.runner import evaluate
from app.simulator.environment import SCENARIOS, SignalConfig, TrafficEnvironment


class CreateRunRequest(BaseModel):
    scenario: str = "balanced"
    controller: str = "fixed_time"
    seed: int = 0
    green_seconds: int = Field(default=20, ge=1, le=120)


class StepRequest(BaseModel):
    steps: int = Field(default=1, ge=1, le=1000)


class EvaluationRequest(BaseModel):
    scenarios: list[str] = Field(default_factory=lambda: ["balanced", "rush_hour", "north_surge"], min_length=1, max_length=3)
    seeds: list[int] = Field(default_factory=lambda: [101, 202, 303], min_length=1, max_length=30)
    steps: int = Field(default=500, ge=1, le=10000)


@dataclass
class Run:
    env: TrafficEnvironment
    controller: str
    fixed: FixedTimeController
    agent: QLearningAgent
    paused: bool = True


runs: dict[str, Run] = {}
router = APIRouter(prefix="/api")


def serialize_snapshot(run: Run) -> dict:
    snap = run.env.snapshot()
    return {
        "time": snap.time,
        "phase": snap.phase.value,
        "transitioning": snap.transitioning,
        "phase_elapsed": snap.phase_elapsed,
        "queues": {approach.value: count for approach, count in snap.queues.items()},
        "arrived": snap.arrived,
        "served": snap.served,
        "total_wait_seconds": snap.total_wait_seconds,
        "average_wait_seconds": snap.average_wait_seconds,
        "max_queue": snap.max_total_queue,
        "paused": run.paused,
        "controller": run.controller,
    }


@router.get("/health")
def health():
    return {"status": "ok", "service": "smart-traffic-ai"}


@router.get("/scenarios")
def scenarios():
    return [{"name": s.name, "arrival_rates": {a.value: rate for a, rate in s.arrival_rates.items()}}
            for s in SCENARIOS.values()]


@router.post("/runs")
def create_run(request: CreateRunRequest):
    if request.scenario not in SCENARIOS:
        raise HTTPException(422, f"unknown scenario: {request.scenario}")
    if request.controller not in {"fixed_time", "q_learning"}:
        raise HTTPException(422, "controller must be fixed_time or q_learning")
    config = SignalConfig(max_green=max(30, request.green_seconds))
    green = min(request.green_seconds, config.max_green)
    run_id = str(uuid4())
    run = Run(TrafficEnvironment(SCENARIOS[request.scenario], request.seed, config),
              request.controller, FixedTimeController(green, config), QLearningAgent(epsilon=0))
    runs[run_id] = run
    return {"id": run_id, **serialize_snapshot(run)}


@router.get("/runs/{run_id}")
def get_run(run_id: str):
    run = runs.get(run_id)
    if run is None:
        raise HTTPException(404, "run not found")
    return serialize_snapshot(run)


@router.post("/runs/{run_id}/step")
def step_run(run_id: str, request: StepRequest):
    run = runs.get(run_id)
    if run is None:
        raise HTTPException(404, "run not found")
    for _ in range(request.steps):
        if run.controller == "fixed_time":
            run.fixed.step(run.env)
        else:
            action = run.agent.act(run.env)
            if action == 1:
                run.env.request_switch()
            run.env.step()
    return serialize_snapshot(run)


@router.post("/runs/{run_id}/control/{action}")
def control_run(run_id: str, action: str):
    run = runs.get(run_id)
    if run is None:
        raise HTTPException(404, "run not found")
    if action == "pause":
        run.paused = True
    elif action == "resume":
        run.paused = False
    elif action == "reset":
        run.env.reset()
        run.paused = True
    else:
        raise HTTPException(404, "action must be pause, resume, or reset")
    return serialize_snapshot(run)


@router.post("/evaluations")
def run_evaluation(request: EvaluationRequest):
    unknown = set(request.scenarios) - set(SCENARIOS)
    if unknown:
        raise HTTPException(422, f"unknown scenarios: {', '.join(sorted(unknown))}")
    return evaluate([SCENARIOS[name] for name in request.scenarios], request.seeds,
                    request.steps, SignalConfig(), QLearningAgent(epsilon=0))


app = FastAPI(title="Smart Traffic AI", version="0.1.0",
              description="Educational four-way traffic signal simulator API")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:4173", "http://localhost:4173"],
                   allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
app.include_router(router)
