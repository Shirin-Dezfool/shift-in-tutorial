# snip — quality characteristics

Prioritised for this service (ISO/IEC 25010 framing), highest first.

1. **Functional correctness** — a short link always resolves to the exact URL it was created for;
   click counts are accurate.
2. **Performance efficiency** — following a link is the hot path and must be fast.
3. **Reliability / availability** — the redirect path must stay up; creating links can tolerate
   brief degradation.
4. **Security** — only safe, well-formed URLs are accepted; no open-redirect or script-scheme abuse.
5. **Maintainability** — small, well-tested codebase that an agent and a human can both reason about.

## Notes that shape the test strategy

- The **follow/redirect** path dominates traffic — weight test and SLI effort there.
- **Create** is lower volume but is where input-validation and security risks live.
- Stats accuracy depends on the follow path incrementing reliably.
