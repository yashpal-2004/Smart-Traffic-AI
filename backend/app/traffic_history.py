"""Persistent traffic observations and a small, auditable one-step forecaster."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
import os
from pathlib import Path
import sqlite3
from statistics import median


DEFAULT_DB = Path(__file__).resolve().parents[1] / "data" / "traffic_history.sqlite3"


def _db_path() -> Path:
    return Path(os.environ.get("TRAFFIC_HISTORY_DB", DEFAULT_DB))


def _connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("""CREATE TABLE IF NOT EXISTS observations (
        site_id TEXT NOT NULL,
        recorded_at TEXT NOT NULL,
        captured_at TEXT NOT NULL,
        measured_vehicles_per_cycle REAL NOT NULL,
        occupancy_percent REAL,
        lane_count INTEGER NOT NULL,
        PRIMARY KEY (site_id, recorded_at)
    )""")
    connection.execute("CREATE INDEX IF NOT EXISTS observations_by_site_time ON observations(site_id, recorded_at)")
    return connection


def save_snapshot(feed: dict) -> dict:
    """Persist each unique provider timestamp/site pair; return insertion counts."""
    captured_at = feed.get("retrieved_at") or datetime.now(timezone.utc).isoformat()
    inserted = 0
    skipped = 0
    with _connect() as connection:
        for site in feed.get("sites", []):
            recorded_at = site.get("recorded_at")
            if not recorded_at:
                skipped += 1
                continue
            cursor = connection.execute(
                """INSERT OR IGNORE INTO observations
                (site_id, recorded_at, captured_at, measured_vehicles_per_cycle,
                 occupancy_percent, lane_count) VALUES (?, ?, ?, ?, ?, ?)""",
                (str(site["site_id"]), str(recorded_at), captured_at,
                 float(site.get("measured_vehicles_per_cycle") or 0),
                 site.get("average_detector_occupancy_percent"), int(site.get("lane_count") or 0)),
            )
            inserted += cursor.rowcount
            skipped += 1 - cursor.rowcount
    return {"inserted": inserted, "already_present_or_missing_timestamp": skipped,
            "captured_at": captured_at, "source_recorded_at": feed.get("latest_recorded_at")}


def history_summary() -> dict:
    with _connect() as connection:
        rows = connection.execute("""SELECT site_id, COUNT(*) AS observations,
            MIN(recorded_at) AS first_recorded_at, MAX(recorded_at) AS latest_recorded_at
            FROM observations GROUP BY site_id ORDER BY site_id""").fetchall()
    return {"total_observations": sum(row["observations"] for row in rows),
            "site_count": len(rows), "sites": [dict(row) for row in rows]}


def site_history(site_id: str, limit: int = 500) -> list[dict]:
    with _connect() as connection:
        rows = connection.execute("""SELECT site_id, recorded_at, captured_at,
            measured_vehicles_per_cycle, occupancy_percent, lane_count
            FROM observations WHERE site_id = ? ORDER BY recorded_at DESC LIMIT ?""",
            (str(site_id), max(1, min(limit, 2000)))).fetchall()
    return [dict(row) for row in reversed(rows)]


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _features(history: list[dict], target_index: int, target_time: datetime) -> list[float]:
    values = [float(row["measured_vehicles_per_cycle"]) for row in history]
    hour = target_time.hour + target_time.minute / 60
    angle = 2 * math.pi * hour / 24
    return [1.0, values[target_index - 1], values[target_index - 2], values[target_index - 3],
            math.sin(angle), math.cos(angle)]


def _solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    """Solve a tiny dense system by Gaussian elimination with pivoting."""
    size = len(vector)
    augmented = [row[:] + [value] for row, value in zip(matrix, vector)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise ValueError("forecast features are singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [left - factor * right for left, right in zip(augmented[row], augmented[column])]
    return [augmented[row][-1] for row in range(size)]


def _fit(rows: list[dict], stop: int) -> list[float]:
    width = 6
    gram = [[0.0] * width for _ in range(width)]
    rhs = [0.0] * width
    for index in range(3, stop):
        timestamp = _parse_time(rows[index]["recorded_at"])
        features = _features(rows, index, timestamp)
        target = float(rows[index]["measured_vehicles_per_cycle"])
        for i in range(width):
            rhs[i] += features[i] * target
            for j in range(width):
                gram[i][j] += features[i] * features[j]
    for diagonal in range(1, width):
        gram[diagonal][diagonal] += 0.01
    return _solve(gram, rhs)


def _predict(coefficients: list[float], features: list[float]) -> float:
    return max(0.0, sum(coefficient * feature for coefficient, feature in zip(coefficients, features)))


def _metrics(actual: list[float], predicted: list[float]) -> dict:
    if not actual:
        return {"mae": None, "rmse": None, "sample_count": 0}
    errors = [guess - truth for truth, guess in zip(actual, predicted)]
    return {"mae": round(sum(abs(error) for error in errors) / len(errors), 3),
            "rmse": round(math.sqrt(sum(error * error for error in errors) / len(errors)), 3),
            "sample_count": len(errors)}


def forecast_site(site_id: str, minimum_observations: int = 24) -> dict:
    """Walk-forward time split evaluation plus the next-cycle estimate.

    Model: ridge-regularized linear regression over three previous cycle counts
    and cyclical time-of-day. Validation predicts each held-out point from only
    the previous observed values; comparison baseline carries the latest value.
    """
    rows = site_history(site_id, limit=2000)
    count = len(rows)
    if count < minimum_observations:
        return {"status": "insufficient_data", "site_id": str(site_id), "observation_count": count,
                "minimum_observations": minimum_observations, "history": rows[-120:]}

    split = max(4, int(count * 0.8))
    if count - split < 2 or split <= 6:
        return {"status": "insufficient_data", "site_id": str(site_id), "observation_count": count,
                "minimum_observations": max(minimum_observations, 9), "history": rows[-120:]}

    coefficients = _fit(rows, split)
    actual: list[float] = []
    baseline: list[float] = []
    predicted: list[float] = []
    validation = []
    for index in range(split, count):
        timestamp = _parse_time(rows[index]["recorded_at"])
        features = _features(rows, index, timestamp)
        truth = float(rows[index]["measured_vehicles_per_cycle"])
        naive = float(rows[index - 1]["measured_vehicles_per_cycle"])
        model_value = _predict(coefficients, features)
        actual.append(truth)
        baseline.append(naive)
        predicted.append(model_value)
        validation.append({"recorded_at": rows[index]["recorded_at"], "actual": round(truth, 3),
                           "naive": round(naive, 3), "model": round(model_value, 3)})

    last_time = _parse_time(rows[-1]["recorded_at"])
    intervals = [(_parse_time(rows[i]["recorded_at"]) - _parse_time(rows[i - 1]["recorded_at"])).total_seconds()
                 for i in range(1, count)]
    intervals = [seconds for seconds in intervals if seconds > 0]
    next_interval = median(intervals) if intervals else 60
    target_time = last_time + timedelta(seconds=next_interval)
    live_features = _features(rows, count, target_time)
    full_coefficients = _fit(rows, count)
    return {"status": "ready", "site_id": str(site_id), "observation_count": count,
            "validation_method": "chronological holdout (last 20%), one-step rolling prediction",
            "validation_start": rows[split]["recorded_at"], "validation_end": rows[-1]["recorded_at"],
            "metrics": {"persistence_baseline": _metrics(actual, baseline),
                        "ridge_regression": _metrics(actual, predicted)},
            "validation": validation[-120:],
            "next_cycle_forecast": {"estimated_for": target_time.isoformat(),
                                     "estimated_interval_seconds": round(next_interval),
                                     "persistence_baseline": round(float(rows[-1]["measured_vehicles_per_cycle"]), 3),
                                     "ridge_regression": round(_predict(full_coefficients, live_features), 3)},
            "history": rows[-120:],
            "model": {"name": "Ridge-regularized linear regression", "features": ["previous cycle count (lag 1)",
                       "previous cycle count (lag 2)", "previous cycle count (lag 3)",
                       "hour of day sine", "hour of day cosine"], "regularization": 0.01}}
