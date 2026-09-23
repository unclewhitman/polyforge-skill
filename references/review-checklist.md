# PolyForge final review checklist

- Scope: only approved files/systems changed; unexpected changes explained.
- Contracts: signatures, data shapes, compatibility and edge conditions match the approved spec.
- Acceptance: every criterion has real evidence; test/build/lint/typecheck results are from the orchestrator.
- Quality: regressions, silent failures, security risks, concurrency/migration risks (when relevant), and integration gaps are checked.
- Evidence: claims without reproducible evidence do not pass.

Verdict: `ship`, `fix-first`, or `rethink`.
