"""Locust load test for the VeritasAD API (thesis sec. 4.2).

Simulates concurrent users hitting the read-mostly endpoints (history, task
status) plus an occasional analysis submission, so the report's latency / RPS /
error-rate table reflects a real run rather than a hand-written estimate.

Run (100 users, 10/s spawn, 10 minutes)::

    locust -f tests/load/locustfile.py \
        --host http://localhost:8000 \
        -u 100 -r 10 -t 10m --headless --csv=locust_report

Authentication: set ``VERITAS_TOKEN`` (a Bearer access token) or
``VERITAS_API_KEY`` in the environment. Without either, requests run
unauthenticated to measure raw routing/error behaviour.
"""
import os
import random

from locust import HttpUser, between, task


def _auth_headers() -> dict:
    token = os.getenv("VERITAS_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    api_key = os.getenv("VERITAS_API_KEY")
    if api_key:
        return {"X-API-Key": api_key}
    return {}


class VeritasUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self) -> None:
        self.headers = _auth_headers()
        # Seed of plausible task ids to poll for status.
        self.task_ids = [f"task-{i}" for i in range(1, 6)]

    @task(5)
    def health(self) -> None:
        self.client.get("/health", name="GET /health")

    @task(8)
    def history(self) -> None:
        self.client.get(
            "/api/v1/analyze/history?limit=20&offset=0",
            headers=self.headers,
            name="GET /api/v1/analyze/history",
        )

    @task(6)
    def task_status(self) -> None:
        task_id = random.choice(self.task_ids)
        self.client.get(
            f"/api/v1/analysis/{task_id}/status",
            headers=self.headers,
            name="GET /api/v1/analysis/{task_id}/status",
        )

    @task(2)
    def analyze_by_task(self) -> None:
        task_id = random.choice(self.task_ids)
        self.client.get(
            f"/api/v1/analyze/{task_id}",
            headers=self.headers,
            name="GET /api/v1/analyze/{task_id}",
        )
