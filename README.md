# snip

A tiny URL shortener — the **starter application** for the Shift In tutorial. This is the `start`
state: it runs, but it has **no tests, no CI, and no AI tooling yet**. That is the point.

## Before the workshop

Do this a few days out, not on the morning of:

1. Install and authenticate Claude Code with your own Claude subscription; clone this repo.
2. Connect GitHub MCP under your own GitHub account — this is a one-time setup, not something
   you'll do live on the day:
   ```bash
   claude mcp add --transport http github https://api.githubcopilot.com/mcp/
   ```
   The first time Claude Code actually needs a GitHub tool, it'll prompt you to authenticate
   (`/mcp` inside a session, or it'll ask automatically) — one browser click to authorize, done.
   Confirm it worked with `claude mcp list`: `github` should show as connected.
3. Run one smoke prompt — e.g. ask Claude Code to read this file and summarize it — to confirm
   everything's wired up before the room fills.

## Run it

```bash
pip install -e .
uvicorn snip.main:app --reload --app-dir src
```

- Interactive docs: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/links` | Create a short link from `{ "url": "..." }` |
| GET | `/api/links` | List links |
| GET | `/api/links/{code}/stats` | Click stats for a code |
| GET | `/{code}` | Follow a short link (redirect) |

## Where to look

- `docs/business-context.md`, `docs/quality-characteristics.md`, `docs/slis.md` — what "good" means.
- `src/snip/` — the implementation.
- `tests/` — empty on purpose; you add tests during the workshop.
