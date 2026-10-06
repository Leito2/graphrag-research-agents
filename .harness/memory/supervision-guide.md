# Supervision guide (human supervisor)

## Gates you own
- **Spec gate:** every requirement uses an EARS pattern, is testable, has a `REQ-xx` id; failure modes are covered
  (no evidence, provider down, search engines blocked, prompt injection in web content, consent off, loop bound).
- **Design gate:** modules match PLAN §12; at least two alternatives with rejection reasons; ADRs recorded.

## Red flags (stop the pipeline)
- A phase transition decided by an LLM call.
- Any code path able to write outside `RESEARCH_OUTPUT_DIR` or to modify an existing note.
- Vault content sent to a cloud provider while `VAULT_CLOUD_CONSENT=false`.
- `requirements.md` edited during `apply`; diffs > 600 lines; EARS requirements missing from `review.md`.

## Health thresholds
| Signal | Healthy | Warning | Critical |
|---|---|---|---|
| Test coverage | ≥ 80% | 60–79% | < 60% |
| EARS coverage in `review.md` | 100% | < 100% | sections missing |
| Diff size per task | < 400 lines | 400–600 | > 600 |
| Context fill per agent | < 20% | 20–40% | > 40% |
