"""Poll Brisbane's public signal-volume feed and store unique source snapshots.

Run from the repository root:
    python3 backend/scripts/collect_traffic_history.py --interval 60
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.traffic_feed import fetch_live_intersections, fetch_site_observations
from app.traffic_history import save_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval", type=int, default=60, help="seconds between collection attempts (minimum 15)")
    parser.add_argument("--site-id", help="collect one controller site; recommended for complete site history")
    args = parser.parse_args()
    interval = max(15, args.interval)
    print(f"Collecting Brisbane traffic snapshots every {interval}s. Press Ctrl+C to stop.", flush=True)
    while True:
        try:
            feed = fetch_site_observations(args.site_id) if args.site_id else fetch_live_intersections()
            result = save_snapshot(feed)
            print(json.dumps({"site_count": feed["site_count"], "record_count": feed["record_count"], **result}), flush=True)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            print(json.dumps({"error": str(exc)}), flush=True)
        time.sleep(interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCollector stopped.", flush=True)
