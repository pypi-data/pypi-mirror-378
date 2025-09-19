"""
Ray-based consumer worker for user profile generation jobs.

Reads pending jobs from DuckDB (user_profile_jobs), runs the internal
profiling Agent to generate a profile, and upserts it to DuckDB.

Usage:
  python -m hou_garden.agents.tools.user_profile_worker --num-workers 1 --interval 0.5

Requires: `pip install duckdb ray`
"""

from __future__ import annotations

import argparse
import os
import time
from typing import Optional

try:
    import ray
except Exception as _e:  # pragma: no cover - optional runtime dep
    ray = None  # type: ignore


def _ensure_ray():  # pragma: no cover
    global ray
    if ray is None:
        raise SystemExit("Ray is not installed. Please `pip install ray`." )
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True, include_dashboard=False)


def _get_tools():
    # Lazy import to avoid heavy deps when running tests
    from hou_garden.agents.tools.user_profile_tools import (
        _jobs_next_pending,
        _jobs_mark,
        user_profile_generate_and_upsert,
    )
    return _jobs_next_pending, _jobs_mark, user_profile_generate_and_upsert


if ray:
    @ray.remote
    class ProfileJobWorker:
        def __init__(self, poll_interval: float = 0.5):
            self.poll_interval = poll_interval

        def run_loop(self):  # pragma: no cover
            _jobs_next_pending, _jobs_mark, user_profile_generate_and_upsert = _get_tools()
            while True:
                jobs = _jobs_next_pending(limit=1)
                if not jobs:
                    time.sleep(self.poll_interval)
                    continue
                job = jobs[0]
                jid = job["job_id"]
                try:
                    _jobs_mark(jid, status="running", error=None, inc_try=True)
                    # sync upsert to guarantee visibility after completion
                    res = user_profile_generate_and_upsert(
                        user_id=job["user_id"],
                        text=job["text"],
                        merge=bool(job.get("merge", True)),
                        sync=True,
                    )
                    if not res.get("ok"):
                        _jobs_mark(jid, status="failed", error=str(res))
                    else:
                        _jobs_mark(jid, status="done", error=None)
                except Exception as e:
                    _jobs_mark(jid, status="failed", error=str(e))


def main():  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-workers", type=int, default=1)
    parser.add_argument("--interval", type=float, default=0.5)
    args = parser.parse_args()

    _ensure_ray()
    workers = [ProfileJobWorker.remote(poll_interval=args.interval) for _ in range(args.num_workers)]
    # Keep processes alive
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":  # pragma: no cover
    main()

