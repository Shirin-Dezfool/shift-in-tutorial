# snip — business context

## What it is

**snip** is an internal URL-shortening service. Teams across the company paste long, ugly links
into chat, docs, and slides; snip turns them into short, shareable codes and counts how often each
short link is followed.

## Who uses it

- **Employees** creating short links for internal docs and dashboards.
- **Recipients** following short links (the highest-volume path by far).
- **Link owners** checking how many times their link was followed.

## Core capabilities (current)

1. Create a short link from a long URL.
2. Follow a short link (redirect to the original URL).
3. List existing links.
4. See click stats for a link.

## Definition of Ready (DoR) — excerpt

- The user story has a clear actor, action, and outcome.
- Acceptance criteria are testable and agreed by the Three Amigos.
- Impact on the published SLIs is understood.

## Definition of Done (DoD) — excerpt

- Code reviewed and merged via PR.
- Tests exist at the appropriate level(s) and pass in CI.
- SLI-affecting changes are reflected in the pipeline gates.
- Observable behaviour changes are covered by at least one higher-level test.

## Known roadmap item (used in M5)

**Link expiry:** owners want links that stop working after a chosen time. This is the feature
built during the M5 finale via Example Mapping + an agent build.
