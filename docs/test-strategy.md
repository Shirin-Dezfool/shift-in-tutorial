# snip — test strategy (v1)

Status: **target**. No tests exist yet; this is what we will be held to. It derives from
`business-context.md`, `quality-characteristics.md` and `slis.md`. Revise it when the SLIs or
priorities change, and note the change in the PR.

## Principles

- **Weight follows traffic and risk.** `GET /{code}` dominates traffic and carries SLIs 1–3, so it
  gets the most test effort. Create (`POST /api/links`) is lower volume but is where validation and
  security risk lives (SLI 4). Stats accuracy (SLI 5) depends on the follow path counting reliably.
- **Correctness first, then speed, then availability, then security, then maintainability** — the
  order of `quality-characteristics.md`. When effort is limited, spend it in that order.
- **Prove each SLI at the cheapest level that can actually prove it.** A level that can't observe
  the SLI doesn't count (e.g. a unit test can't prove p95 latency of the running service).
- **Observable behaviour changes need at least one higher-level test** (Definition of Done), not
  only unit tests.
- Tests are part of the change: no merge without tests at the appropriate level, passing in CI.

## Target test pyramid

| Level | What it exercises | Tooling | Target weight (share of test effort) |
|---|---|---|---|
| Unit | Code generation, URL validation rules, store operations, click counting logic, in isolation | pytest, pytest-cov | 50% |
| API / integration | The FastAPI app in-process via its HTTP interface: status codes, bodies, redirects, store wired in | pytest + FastAPI `TestClient` | 30% |
| System (end-to-end) | The real running service over a socket: create → follow → stats journeys | Robot Framework against uvicorn | 15% |
| Performance gate | p95 latency of `GET /{code}` on the running service | scripted load check run in CI | 5% |

Within every level, split effort roughly **60% redirect/follow, 30% create, 10% list/stats**,
matching traffic and risk. System-level coverage is deliberately weighted toward the redirect hot
path (SLIs 1–3).

Coverage (pytest-cov) is a smell detector, not a goal: use it to find untested branches on the
follow and create paths. Coverage percentage alone never proves an SLI.

## SLI → proving test level

| # | SLI | Target | Primary proof (level) | Supporting tests | CI gate |
|---|-----|--------|-----------------------|------------------|---------|
| 1 | Redirect latency | p95 < 50 ms | **Performance gate** — repeated `GET /{code}` against the running service, assert p95 | System journey confirms the measured path is the real one | Yes — fail build if p95 ≥ 50 ms |
| 2 | Redirect availability | ≥ 99.9% valid redirect or correct 404 | **System** — follow known codes and unknown codes against the running service; every response is a redirect or a clean 404 (never a 5xx) | API tests for known/unknown/malformed codes; unit tests on store lookup misses | Yes — any 5xx on the follow path fails the build |
| 3 | Resolve correctness | 100% exact stored URL | **API / integration** — create then follow, assert `Location` equals the submitted URL byte for byte, across a table of awkward URLs (query strings, fragments, encoding, long URLs) | Unit tests on store round-trip; one system journey end to end | Yes — first-choice gate (cheap, exact) |
| 4 | Create validation | 100% invalid/unsafe rejected | **API / integration** — table-driven create requests: malformed, empty, non-http(s) schemes (`javascript:`, `data:`, `file:`), scheme-less, oversized; assert rejection and that nothing is stored | Unit tests on the validation function; one system check that a rejected URL can't be followed | Yes — any accepted unsafe URL fails the build |
| 5 | Stats accuracy | recorded clicks = actual follows | **API / integration** — follow a code N times, assert stats report exactly N; unknown-code follows don't count | Unit tests on the counter; system journey create → follow ×N → stats | Yes — runs with the integration suite |

## Selected examples that must exist before the strategy is "met"

- **Oracle-style checks:** each SLI test asserts against an independently stated expected value
  (the URL we submitted, the count we performed), never against values read back from the code
  under test.
- **Negative paths on follow:** unknown code → 404; malformed code → clean 4xx/404; none produce a 5xx.
- **Hand-mutation sanity check:** for the follow and create paths, deliberately break the code
  (e.g. redirect to the wrong URL, skip the click increment, accept a `javascript:` URL) and
  confirm a test fails. A test that survives the break is not proving the SLI.

## What each level must not do

- Unit tests don't start a server or assert latency.
- API tests don't claim availability or latency: in-process calls say nothing about the real service.
- System tests are few and slow by design: journeys and the redirect hot path, not every input variation.
- The performance gate measures only `GET /{code}`; it is not a general benchmark suite.

## CI expectations (target)

1. Unit + API/integration suites run on every PR; failure blocks merge.
2. System suite runs on every PR against a freshly started service.
3. The performance gate runs on every PR touching the follow path, and nightly.
4. At least one SLI-linked gate (resolve correctness or redirect latency) exists first; the rest
   follow, in SLI order of priority 3, 1, 2, 4, 5 by cost-to-add.
5. A PR that changes an SLI-affecting behaviour must update this table or state "no SLI impact".

## Out of scope for v1

- Load/soak testing beyond the single latency gate.
- Security testing beyond URL validation (SLI 4).
- Link expiry (roadmap): when it's picked up, add its acceptance criteria and SLI impact here
  before building.
