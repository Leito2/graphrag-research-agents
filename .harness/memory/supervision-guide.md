# Supervision guide (human supervisor)

## Gates you own
- **Spec gate:** every requirement uses an EARS pattern, is testable, has a `REQ-xx` id; failure modes are covered
  (no evidence, provider down, quota exhausted, prompt injection in web content, contradiction loop bound).
- **Design gate:** modules match PLAN §12; at least two alternatives with rejection reasons; ADRs recorded.

## Red flags (stop the pipeline)
- A phase transition decided by an LLM call.
- `requirements.md` edited during `apply`.
- A diff > 600 lines without decomposition, or EARS requirements missing from `review.md`.
- Secrets in git history; context fill per agent consistently > 40%.

## Health thresholds
| Signal | Healthy | Warning | Critical |
|---|---|---|---|
| Test coverage | ≥ 80% | 60–79% | < 60% |
| EARS coverage in `review.md` | 100% | < 100% | sections missing |
| Diff size per task | < 400 lines | 400–600 | > 600 |
| Context fill per agent | < 20% | 20–40% | > 40% |
