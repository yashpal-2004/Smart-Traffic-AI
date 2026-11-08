"""Validated API models, in-memory run manager, and routes."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4
from pathlib import Path
from threading import Lock, Thread
from random import Random
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
import re
import subprocess
import sqlite3
from urllib.error import HTTPError, URLError
from typing import Any, Literal

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.agents.fixed_time import FixedTimeController
from app.agents.q_learning import QLearningAgent, train_episode
from app.agents.duration_q_learning import DurationQLearningAgent, DURATIONS, train_duration_episode
from app.evaluation.runner import evaluate
from app.simulator.environment import SCENARIOS, SignalConfig, TrafficEnvironment
from app.traffic_feed import fetch_live_intersections, fetch_site_observations
from app.traffic_history import forecast_site, history_summary, save_snapshot, site_history


class CreateRunRequest(BaseModel):
    scenario: str = "balanced"
    controller: str = "fixed_time"
    engine: Literal["python", "sumo"] = "python"
    sumo_gui: bool = False
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
    env: Any
    controller: str
    fixed: FixedTimeController
    agent: QLearningAgent
    history: list[dict]
    engine: str = "python"
    model_trained: bool = False
    green_target: int | None = None
    paused: bool = True


runs: dict[str, Run] = {}
training_lock = Lock()
training_job: dict = {"status": "idle", "completed": 0, "total": 0}
MODEL_PATH = Path(__file__).resolve().parents[2] / "artifacts" / "q_table.json"
DURATION_MODEL_PATH = Path(__file__).resolve().parents[2] / "artifacts" / "duration_q_table.json"
SUMO_MODEL_PATH = Path(__file__).resolve().parents[2] / "artifacts" / "sumo_q_table.json"
trained_agent = QLearningAgent.load(MODEL_PATH) if MODEL_PATH.exists() else QLearningAgent(epsilon=0, epsilon_min=0)
model_trained = MODEL_PATH.exists()
duration_agent = DurationQLearningAgent.load(DURATION_MODEL_PATH) if DURATION_MODEL_PATH.exists() else None
sumo_agent: QLearningAgent | None = None
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


def load_sumo_agent() -> QLearningAgent | None:
    global sumo_agent
    from app.simulator.sumo.environment import SUMO_ENVIRONMENT_VERSION

    if not SUMO_MODEL_PATH.is_file():
        sumo_agent = None
        return sumo_agent
    try:
        checkpoint = json.loads(SUMO_MODEL_PATH.read_text(encoding="utf-8"))
        if checkpoint.get("sumo_environment_version") != SUMO_ENVIRONMENT_VERSION:
            sumo_agent = None
            return sumo_agent
        sumo_agent = QLearningAgent.load(SUMO_MODEL_PATH)
    except (OSError, ValueError, TypeError):
        sumo_agent = None
    return sumo_agent


def serialize_snapshot(run: Run) -> dict:
    snap = run.env.snapshot()
    visualization = getattr(run.env, "visualization", None)
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
        "engine": run.engine,
        "green_target": run.green_target,
        "history": run.history[-500:],
        "model_trained": run.model_trained,
        "sumo_visualization": visualization() if visualization else None,
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


@router.post("/traffic/history/collect")
def collect_traffic_history(site_id: str | None = None):
    if site_id is not None and not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", site_id):
        raise HTTPException(422, "site_id contains unsupported characters")
    try:
        feed = fetch_site_observations(site_id) if site_id else fetch_live_intersections()
        stored = save_snapshot(feed)
        return {**stored, "site_count": feed["site_count"], "record_count": feed["record_count"],
                "source": feed["source"], "history": history_summary()}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except (HTTPError, URLError, TimeoutError, OSError, sqlite3.Error) as exc:
        raise HTTPException(503, f"Traffic history collection failed: {exc}") from exc


@router.get("/traffic/history")
def get_traffic_history(site_id: str | None = None, limit: int = 500):
    try:
        summary = history_summary()
        return {**summary, "selected_site": site_id,
                "observations": site_history(site_id, limit) if site_id else []}
    except sqlite3.Error as exc:
        raise HTTPException(503, f"Traffic history storage is unavailable: {exc}") from exc


@router.get("/traffic/forecast")
def get_traffic_forecast(site_id: str):
    try:
        report = forecast_site(site_id)
    except (sqlite3.Error, ValueError) as exc:
        raise HTTPException(422, f"Unable to forecast site {site_id}: {exc}") from exc
    if report["status"] == "insufficient_data":
        return report
    return report


@router.get("/scenarios")
def scenarios():
    return [{"name": s.name, "arrival_rates": {a.value: rate for a, rate in s.arrival_rates.items()}}
            for s in SCENARIOS.values()]


@router.get("/simulators")
def simulators():
    from importlib.util import find_spec
    from app.simulator.sumo.environment import _binary, sumo_gui_status

    sumo_available = (find_spec("traci") is not None and bool(_binary("sumo"))
                      and bool(_binary("netconvert")))
    sumo_gui_available, sumo_gui_message = sumo_gui_status()
    sumo_gui_available = find_spec("traci") is not None and sumo_gui_available
    sumo_policy = load_sumo_agent()
    return {
        "simulators": [
            {"id": "python", "name": "Python traffic model", "available": True},
            {"id": "sumo", "name": "Eclipse SUMO", "available": sumo_available},
        ],
        "sumo_model_trained": sumo_policy is not None,
        "sumo_gui_available": sumo_gui_available,
        "sumo_gui_message": sumo_gui_message,
    }


@router.post("/runs")
def create_run(request: CreateRunRequest):
    if request.scenario not in SCENARIOS:
        raise HTTPException(422, f"unknown scenario: {request.scenario}")
    if request.controller not in {"fixed_time", "q_learning", "duration_q_learning"}:
        raise HTTPException(422, "unknown controller")
    if request.controller == "duration_q_learning" and duration_agent is None:
        raise HTTPException(409, "train the duration Q-learning model before using it")
    if request.engine == "sumo" and request.controller == "duration_q_learning":
        raise HTTPException(422, "green-duration Q-learning is not available in the SUMO simulator yet")
    sumo_policy = load_sumo_agent() if request.engine == "sumo" else None
    if request.engine == "sumo" and request.controller == "q_learning" and sumo_policy is None:
        raise HTTPException(409, "No compatible SUMO-trained Q-table found. Rerun the SUMO evaluation script to train one.")
    if request.engine == "sumo" and request.sumo_gui:
        gui_status = simulators()
        if not gui_status["sumo_gui_available"]:
            raise HTTPException(503, gui_status["sumo_gui_message"] or "SUMO's desktop viewer is unavailable.")
    config = SignalConfig(max_green=max(30, request.green_seconds))
    green = min(request.green_seconds, config.max_green)
    run_id = str(uuid4())
    agent = (sumo_policy if request.engine == "sumo" else
             duration_agent if request.controller == "duration_q_learning" else trained_agent)
    if request.engine == "sumo":
        from app.simulator.sumo.environment import SumoEnvironment
        if not simulators()["simulators"][1]["available"]:
            raise HTTPException(503, "SUMO is unavailable. Install backend/requirements-sumo.txt and ensure sumo and netconvert are available.")
        try:
            env = SumoEnvironment(SCENARIOS[request.scenario], request.seed, config,
                                  steps=1_000_000, gui=request.sumo_gui)
        except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
            raise HTTPException(503, str(exc)) from exc
    else:
        env = TrafficEnvironment(SCENARIOS[request.scenario], request.seed, config)
    run = Run(env, request.controller, FixedTimeController(green, config), agent, [],
              engine=request.engine,
              model_trained=(sumo_policy is not None if request.engine == "sumo" else
                             duration_agent is not None if request.controller == "duration_q_learning" else model_trained))
    runs[run_id] = run
    return {"id": run_id, **serialize_snapshot(run)}


@router.get("/runs/{run_id}")
def get_run(run_id: str):
    run = runs.get(run_id)
    if run is None:
        raise HTTPException(404, "run not found")
    return serialize_snapshot(run)


@router.delete("/runs/{run_id}")
def delete_run(run_id: str):
    run = runs.pop(run_id, None)
    if run is None:
        raise HTTPException(404, "run not found")
    close = getattr(run.env, "close", None)
    if close:
        close()
    return {"deleted": True}


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
                            "wait": snap.average_wait_seconds, "served": snap.served,
                            "phase": snap.phase.value, "transitioning": snap.transitioning})
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
    sumo_policy = load_sumo_agent()
    return {"trained": model_trained, "states": len(trained_agent.q_values),
            "duration_trained": duration_agent is not None,
            "duration_states": len(duration_agent.q_values) if duration_agent else 0,
            "sumo_trained": sumo_policy is not None,
            "sumo_states": len(sumo_policy.q_values) if sumo_policy else 0}


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
                   allow_methods=["GET", "POST", "DELETE"], allow_headers=["Content-Type"])
app.include_router(router)
FRONTEND_DIR = Path(__file__).resolve().parents[3] / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
