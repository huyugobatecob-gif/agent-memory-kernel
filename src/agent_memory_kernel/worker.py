"""Keeper worker loop helpers."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

from .store import MemoryStore


def run_keeper_worker_daemon(
    db_path: str | Path,
    *,
    limit: int = 10,
    actor: str = "worker",
    poll_interval: float = 5.0,
    max_iterations: int | None = None,
    stop_when_idle: bool = False,
    sleep_func: Callable[[float], None] | None = None,
    emit: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Poll queued Keeper jobs until stopped by policy or interruption.

    `max_iterations` and `stop_when_idle` make the loop testable and useful for
    supervised runs. Production services can omit both and let the process run
    until it receives KeyboardInterrupt or its supervisor stops it.
    """
    interval = max(0.0, float(poll_interval or 0.0))
    sleep = sleep_func or time.sleep
    iteration = 0
    processed_total = 0
    idle_iterations = 0
    reports: list[dict[str, Any]] = []
    stopped_reason = "max_iterations" if max_iterations == 0 else "running"

    try:
        while True:
            if max_iterations is not None and iteration >= max(0, int(max_iterations)):
                stopped_reason = "max_iterations"
                break

            iteration += 1
            store = MemoryStore(db_path)
            store.init_db()
            try:
                result = store.process_keeper_jobs(limit=limit, actor=actor)
            finally:
                store.close()

            processed = int(result.get("processed", 0) or 0)
            processed_total += processed
            if processed == 0:
                idle_iterations += 1
            else:
                idle_iterations = 0

            report = {
                "iteration": iteration,
                "processed": processed,
                "processed_total": processed_total,
                "idle_iterations": idle_iterations,
                "jobs": result.get("jobs", []),
            }
            reports.append(report)
            if emit is not None:
                emit(report)

            if stop_when_idle and processed == 0:
                stopped_reason = "idle"
                break
            if max_iterations is not None and iteration >= max(0, int(max_iterations)):
                stopped_reason = "max_iterations"
                break

            sleep(interval)
    except KeyboardInterrupt:
        stopped_reason = "interrupted"

    return {
        "mode": "daemon",
        "status": "stopped",
        "stopped_reason": stopped_reason,
        "iterations": iteration,
        "processed_total": processed_total,
        "idle_iterations": idle_iterations,
        "limit": max(1, min(int(limit or 10), 100)),
        "actor": actor,
        "poll_interval": interval,
        "reports": reports,
    }
