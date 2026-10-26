"""CI gate for SLI 1 (docs/slis.md): p95 server time to answer GET /{code} < 50 ms.

Starts a real uvicorn server, creates one link, follows it REQUESTS times and checks the p95.
"""

import http.client
import json
import math
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SLO_P95_MS = 50  # docs/slis.md, SLI 1: p95 < 50 ms
REQUESTS = 200
WARMUP = 10


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server_port():
    port = free_port()
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn", "snip.main:app",
            "--app-dir", str(ROOT / "src"),
            "--host", "127.0.0.1", "--port", str(port),
            "--log-level", "warning",
        ],
        cwd=ROOT,
    )
    try:
        deadline = time.monotonic() + 15
        while True:
            try:
                socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
                break
            except OSError:
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError("uvicorn did not start")
                time.sleep(0.1)
        yield port
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def p95(samples_ms: list[float]) -> float:
    ordered = sorted(samples_ms)
    return ordered[math.ceil(0.95 * len(ordered)) - 1]  # nearest-rank


def test_redirect_p95_latency_is_under_slo(server_port, capsys):
    conn = http.client.HTTPConnection("127.0.0.1", server_port)
    conn.request(
        "POST", "/api/links",
        body=json.dumps({"url": "https://example.com/latency"}),
        headers={"content-type": "application/json"},
    )
    created = conn.getresponse()
    code = json.loads(created.read())["code"]
    assert created.status == 201

    samples_ms = []
    for i in range(WARMUP + REQUESTS):
        start = time.perf_counter()
        conn.request("GET", f"/{code}")  # http.client does not follow redirects
        response = conn.getresponse()
        response.read()
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert response.status == 307
        if i >= WARMUP:
            samples_ms.append(elapsed_ms)
    conn.close()

    measured = p95(samples_ms)
    with capsys.disabled():
        print(
            f"\nredirect p95 = {measured:.2f} ms over {REQUESTS} follows "
            f"(SLO < {SLO_P95_MS} ms, margin {SLO_P95_MS - measured:.2f} ms)"
        )
    assert measured < SLO_P95_MS, f"p95 {measured:.2f} ms >= SLO {SLO_P95_MS} ms"
