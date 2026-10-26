# CLAUDE.md — snip

snip is an internal URL-shortening service: it turns long links into short codes and counts how
often each short link is followed. Business context, quality priorities and SLIs live in `docs/`
(`business-context.md`, `quality-characteristics.md`, `slis.md`). This file distils them; if they
disagree, the docs win and this file needs updating.

## Who the service serves (priority order)

1. **Recipients following short links** — highest volume by far. The redirect path is the product.
2. **Employees creating short links** — lower volume, but where input-validation and security risk lives.
3. **Link owners checking click stats** — depends on the follow path counting reliably.

When trade-offs arise, protect the follow path first, then create, then list/stats.

## Quality bar (highest priority first)

1. **Functional correctness** — a short link always resolves to the exact URL it was created for;
   click counts are accurate.
2. **Performance efficiency** — following a link is the hot path and must be fast.
3. **Reliability / availability** — the redirect path must stay up; create may tolerate brief degradation.
4. **Security** — accept only safe, well-formed URLs; no open-redirect or script-scheme abuse.
5. **Maintainability** — small, well-tested code that an agent and a human can both reason about.

Weight test and review effort toward `GET /{code}`. Put validation/security scrutiny on create.

## SLIs (the target, not a description of current code)

| # | SLI | Definition | Target |
|---|-----|------------|--------|
| 1 | Redirect latency | p95 server time for `GET /{code}` | < 50 ms |
| 2 | Redirect availability | `GET /{code}` returns a valid redirect or a correct 404 | ≥ 99.9% |
| 3 | Resolve correctness | follows redirecting to the exact stored URL | 100% |
| 4 | Create validation | invalid/unsafe URLs correctly rejected on create | 100% |
| 5 | Stats accuracy | recorded clicks equal actual follows | 100% |

SLIs 1–3 cover the redirect hot path and get the most test weight. Any change that could move an
SLI must say which one, and the pipeline gates must reflect it.

## Working agreements

- **Definition of Ready:** a story has a clear actor, action and outcome; acceptance criteria are
  testable and agreed by the Three Amigos; impact on the SLIs is understood. If a request doesn't
  say which of SLIs 1–5 it touches, ask before building.
- **Definition of Done:** code reviewed and merged via PR; tests exist at the appropriate level(s)
  and pass in CI; SLI-affecting changes are reflected in pipeline gates; observable behaviour
  changes are covered by at least one higher-level test (not only unit tests).
- State which of SLIs 1–5 a PR affects in its description, including "none".
- Treat SLI-affecting changes to the redirect path (latency, correctness, availability) as
  high-risk: call them out explicitly and don't bundle them with unrelated edits.
- SLIs 3, 4 and 5 target 100%: never relax an exact-URL, rejection or click-count assertion to
  make a change pass (e.g. loosening the `Location` check, or letting a `javascript:` URL through).
  Surface the conflict instead.
- A turn never ends with a failing test: if a test is red, fix it or say clearly that you could not.
- Roadmap item: link expiry (links that stop working after an owner-chosen time). Its SLI impact
  belongs in the acceptance criteria.

## Stack conventions

- Python 3.11+, FastAPI app served by uvicorn. Source lives in `src/snip/` (src layout, packaged
  with hatchling); `main.py` is the app, `models.py` the request/response models, `shortener.py`
  code generation, `store.py` storage.
- Run: create a venv, `pip install -e .`, then `uvicorn snip.main:app --reload --app-dir src`.
- Test: `pip install -e ".[test]"`, then `pytest tests/unit tests/api` (add `--cov=snip` for coverage).
- Runtime dependencies are only `fastapi` and `uvicorn`; keep it that way unless the hot path
  needs more. Test tooling (pytest, pytest-cov, robotframework) is declared separately.
- Endpoints: `POST /api/links`, `GET /api/links`, `GET /api/links/{code}/stats`, `GET /{code}`.
  `GET /{code}` is a catch-all route, so new routes must not shadow it and it must not shadow them.
