# snip — Service Level Indicators (SLIs)

These SLIs define "good" for snip. They drive **what we test** and **what CI gates on**.
Targets are deliberately modest so a workshop pipeline can check them.

| # | SLI | Definition | Target (SLO) |
|---|-----|------------|--------------|
| 1 | **Redirect latency** | p95 server time to answer `GET /{code}` | < 50 ms |
| 2 | **Redirect availability** | share of `GET /{code}` returning a valid redirect or a correct 404 | ≥ 99.9% |
| 3 | **Resolve correctness** | share of follows that redirect to the exact stored URL | 100% |
| 4 | **Create validation** | share of create requests with invalid/unsafe URLs that are correctly rejected | 100% |
| 5 | **Stats accuracy** | recorded clicks equal actual follows | 100% |

## How these map into the workshop

- **M1** references these in the test strategy.
- **M3b** turns at least one SLI into a **CI gate** (latency or correctness are the easy first choices).
- **M4** weights system test coverage toward the redirect hot path (SLIs 1–3).
- **M5** treats SLI impact as part of the feature's acceptance criteria.

> Note: `start` doesn't meet every SLI here yet. Which ones, and why, is exactly what M2's review
> is for — treat this table as the target, not a description of the current code, and don't go
> looking for the specific gaps yourself before then.
