"""Validated API models, in-memory run manager, and routes."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4
from pathlib import Path
from threading import Lock, Thread
from random import Random
from datetime import datetime, timezone
from hashlib import sha256
import os
import subprocess
from urllib.error import HTTPError, URLError

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.agents.fixed_time import FixedTimeController
from app.agents.q_learning import QLearningAgent, train_episode
from app.agents.duration_q_learning import DurationQLearningAgent, DURATIONS, train_duration_episode
from app.evaluation.runner import evaluate
from app.simulator.environment import SCENARIOS, SignalConfig, TrafficEnvironment
from app.traffic_feed import fetch_live_intersections


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


class TrainRequest(BaseModel):
    episodes: int = Field(default=300, ge=1, le=5000)
    steps: int = Field(default=500, ge=50, le=5000)


@dataclass
class Run:
    env: TrafficEnvironment
    controller: str
    fixed: FixedTimeController
    agent: QLearningAgent
    history: list[dict]
    green_target: int | None = None
    paused: bool = True


runs: dict[str, Run] = {}
training_lock = Lock()
training_job: dict = {"status": "idle", "completed": 0, "total": 0}
MODEL_PATH = Path(__file__).resolve().parents[2] / "artifacts" / "q_table.json"
DURATION_MODEL_PATH = Path(__file__).resolve().parents[2] / "artifacts" / "duration_q_table.json"
trained_agent = QLearningAgent.load(MODEL_PATH) if MODEL_PATH.exists() else QLearningAgent(epsilon=0, epsilon_min=0)
model_trained = MODEL_PATH.exists()
duration_agent = DurationQLearningAgent.load(DURATION_MODEL_PATH) if DURATION_MODEL_PATH.exists() else None
router = APIRouter(prefix="/api")


def source_revision_metadata() -> dict:
    override = os.environ.get("SMART_TRAFFIC_SOURCE_REVISION")
    if override:
        return {"revision": override, "revision_source": "SMART_TRAFFIC_SOURCE_REVISION",
                "source_working_tree_clean": None}
    repo_root = Path(__file__).resolve().parents[3]
    try:
        revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_root,
                                  check=True, capture_output=True, text=True, timeout=2).stdout.strip()
        status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--",
                                 ".", ":(exclude)graphify-out"], cwd=repo_root,
                                check=True, capture_output=True, text=True, timeout=2).stdout
        return {"revision": revision, "revision_source": "git",
                "source_working_tree_clean": not bool(status.strip())}
    except (OSError, subprocess.SubprocessError):
        return {"revision": None, "revision_source": "unavailable",
                "source_working_tree_clean": None}


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
        "green_target": run.green_target,
        "history": run.history[-500:],
        "model_trained": model_trained,
    }


@router.get("/health")
def health():
    return {"status": "ok", "service": "smart-traffic-ai"}


@router.get("/traffic/live")
def live_traffic():
    try:
        return fetch_live_intersections()
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        raise HTTPException(503, f"Live traffic feed is temporarily unavailable: {exc}") from exc


@router.get("/scenarios")
def scenarios():
    return [{"name": s.name, "arrival_rates": {a.value: rate for a, rate in s.arrival_rates.items()}}
            for s in SCENARIOS.values()]


@router.post("/runs")
def create_run(request: CreateRunRequest):
    if request.scenario not in SCENARIOS:
        raise HTTPException(422, f"unknown scenario: {request.scenario}")
    if request.controller not in {"fixed_time", "q_learning", "duration_q_learning"}:
        raise HTTPException(422, "unknown controller")
    if request.controller == "duration_q_learning" and duration_agent is None:
        raise HTTPException(409, "train the duration Q-learning model before using it")
    config = SignalConfig(max_green=max(30, request.green_seconds))
    green = min(request.green_seconds, config.max_green)
    run_id = str(uuid4())
    run = Run(TrafficEnvironment(SCENARIOS[request.scenario], request.seed, config),
              request.controller, FixedTimeController(green, config),
              duration_agent if request.controller == "duration_q_learning" else trained_agent, [])
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
        elif run.controller == "duration_q_learning":
            if run.env.transitioning:
                run.env.step()
            else:
                if run.green_target is None:
                    action = run.agent.act(run.env, explore=False)
                    run.green_target = DURATIONS[action]
                if run.env.phase_elapsed >= run.green_target:
                    run.env.request_switch()
                    run.green_target = None
                run.env.step()
        else:
            action = run.agent.act(run.env)
            if action == 1:
                run.env.request_switch()
            run.env.step()
        snap = run.env.snapshot()
        run.history.append({"time": snap.time, "queue": sum(snap.queues.values()),
                            "wait": snap.average_wait_seconds, "served": snap.served})
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
        run.history.clear()
        run.green_target = None
        run.paused = True
    else:
        raise HTTPException(404, "action must be pause, resume, or reset")
    return serialize_snapshot(run)


@router.post("/evaluations")
def run_evaluation(request: EvaluationRequest):
    unknown = set(request.scenarios) - set(SCENARIOS)
    if unknown:
        raise HTTPException(422, f"unknown scenarios: {', '.join(sorted(unknown))}")
    config = SignalConfig()
    report = evaluate([SCENARIOS[name] for name in request.scenarios], request.seeds,
                      request.steps, config, trained_agent, duration_agent)
    def fingerprint(path: Path, available: bool) -> str | None:
        if not available or not path.is_file():
            return None
        digest = sha256()
        with path.open("rb") as checkpoint:
            for chunk in iter(lambda: checkpoint.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()
    report["metadata"] = {
        "report_id": str(uuid4()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "endpoint": "POST /api/evaluations",
        "source": source_revision_metadata(),
        "signal_config": {"min_green_seconds": config.min_green,
                           "max_green_seconds": config.max_green,
                           "amber_seconds": config.amber_seconds},
        "scenario_arrival_rates_per_step": {
            name: {approach.value: rate for approach, rate in SCENARIOS[name].arrival_rates.items()}
            for name in request.scenarios
        },
        "model_checkpoints": {
            "hold_switch_q_table_sha256": fingerprint(MODEL_PATH, model_trained),
            "hold_switch_states": len(trained_agent.q_values),
            "duration_q_table_sha256": fingerprint(DURATION_MODEL_PATH, duration_agent is not None),
            "duration_states": len(duration_agent.q_values) if duration_agent else 0,
        },
    }
    report["protocol"]["trained_policy"] = model_trained
    report["protocol"]["model_state_count"] = len(trained_agent.q_values)
    return report


@router.get("/model")
def model_status():
    return {"trained": model_trained, "states": len(trained_agent.q_values),
            "duration_trained": duration_agent is not None,
            "duration_states": len(duration_agent.q_values) if duration_agent else 0}


@router.post("/training")
def train_model(request: TrainRequest):
    if not training_lock.acquire(blocking=False):
        raise HTTPException(409, "training is already running")
    training_job.update(status="queued", completed=0, total=request.episodes, error=None)

    def worker():
        global trained_agent, model_trained, duration_agent
        try:
            training_job.update(status="running")
            agent = QLearningAgent()
            duration_model = DurationQLearningAgent()
            rng = Random(2026)
            scenarios = list(SCENARIOS.values())
            rewards = []
            for episode in range(request.episodes):
                scenario = scenarios[rng.randrange(len(scenarios))]
                env_seed = rng.randrange(1_000_000)
                agent._rng.seed(rng.randrange(1_000_000))
                metrics = train_episode(TrafficEnvironment(scenario, env_seed), agent, request.steps)
                duration_model._rng.seed(rng.randrange(1_000_000))
                train_duration_episode(TrafficEnvironment(scenario, env_seed), duration_model, request.steps)
                rewards.append(metrics["reward"])
                training_job.update(completed=episode + 1, states=len(agent.q_values),
                                    duration_states=len(duration_model.q_values))
            agent.save(MODEL_PATH)
            duration_model.save(DURATION_MODEL_PATH)
            trained_agent, duration_agent, model_trained = agent, duration_model, True
            for run in runs.values():
                run.agent = trained_agent
            training_job.update(status="complete", states=len(agent.q_values),
                                duration_states=len(duration_model.q_values),
                                mean_reward_last_20=sum(rewards[-20:]) / min(20, len(rewards)))
        except Exception as exc:
            training_job.update(status="failed", error=str(exc))
        finally:
            training_lock.release()

    Thread(target=worker, daemon=True).start()
    return {"status": "queued", "episodes": request.episodes, "steps_per_episode": request.steps}


@router.get("/training")
def training_status():
    return {**training_job, "trained_model": model_trained}


app = FastAPI(title="Smart Traffic AI", version="0.1.0",
              description="Educational four-way traffic signal simulator API")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:4173", "http://localhost:4173"],
                   allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
app.include_router(router)
