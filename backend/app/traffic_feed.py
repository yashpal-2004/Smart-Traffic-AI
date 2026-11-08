"""Read-only adapter for Brisbane City Council's live intersection volume feed."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


FEED_URL = "https://data.brisbane.qld.gov.au/api/explore/v2.1/catalog/datasets/traffic-data-at-intersection/records"


def _number(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


def fetch_live_intersections(limit: int = 100) -> dict:
    """Return latest lane records grouped by signal controller/site.

    Brisbane's `mf*` values are vehicles measured during the controller cycle,
    while `ds*` values are detector occupancy percentages. They are not hourly
    counts, and opaque lane IDs are deliberately not mapped to compass directions.
    """
    query = urlencode({"limit": max(1, min(limit, 100)), "order_by": "recorded desc"})
    request = Request(f"{FEED_URL}?{query}", headers={"Accept": "application/json", "User-Agent": "Smart-Traffic-AI/1.0"})
    with urlopen(request, timeout=8) as response:
        payload = json.loads(response.read().decode("utf-8"))

    rows = payload.get("results")
    if not isinstance(rows, list):
        raise ValueError("upstream traffic feed returned an unexpected response")

    by_site: dict[str, dict] = {}
    latest = None
    for row in rows:
        site = str(row.get("tsc") or row.get("dbid") or "unknown")
        recorded = row.get("recorded")
        latest = max(latest or "", str(recorded or "")) or None
        item = by_site.setdefault(site, {"site_id": site, "recorded_at": recorded, "lane_count": 0,
                                         "measured_vehicles_per_cycle": 0.0, "flow_lane_samples": 0,
                                         "average_detector_occupancy_percent": None, "occupancy_lane_samples": 0})
        item["lane_count"] += 1
        flows = [_number(row.get(f"mf{i}")) for i in range(1, 5)]
        valid_flows = [value for value in flows if value is not None]
        item["measured_vehicles_per_cycle"] += sum(valid_flows)
        item["flow_lane_samples"] += len(valid_flows)
        occupancy = [_number(row.get(f"ds{i}")) for i in range(1, 5)]
        valid_occupancy = [value for value in occupancy if value is not None]
        if valid_occupancy:
            current = item["average_detector_occupancy_percent"]
            prior_n = item["occupancy_lane_samples"]
            item["average_detector_occupancy_percent"] = (
                ((current or 0) * prior_n + sum(valid_occupancy)) / (prior_n + len(valid_occupancy))
            )
            item["occupancy_lane_samples"] += len(valid_occupancy)

    sites = sorted(by_site.values(), key=lambda item: item["site_id"])
    for site in sites:
        site["measured_vehicles_per_cycle"] = round(site["measured_vehicles_per_cycle"], 2)
        if site["average_detector_occupancy_percent"] is not None:
            site["average_detector_occupancy_percent"] = round(site["average_detector_occupancy_percent"], 2)
    try:
        feed_time = datetime.fromisoformat(latest.replace("Z", "+00:00")) if latest else None
        age_seconds = max(0, int((datetime.now(timezone.utc) - feed_time.astimezone(timezone.utc)).total_seconds())) if feed_time else None
    except (TypeError, ValueError):
        age_seconds = None
    return {"source": "Brisbane City Council", "source_url": "https://data.brisbane.qld.gov.au/explore/dataset/traffic-data-at-intersection/",
            "license": "CC BY 4.0", "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "latest_recorded_at": latest, "age_seconds": age_seconds,
            "record_count": len(rows), "site_count": len(sites), "sites": sites,
            "measurement_note": "Measured vehicles are reported per signal-controller cycle; occupancy is detector occupancy percent. Lane IDs are not compass directions."}
