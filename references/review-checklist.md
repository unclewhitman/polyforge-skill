# PolyForge optional review

Use when independent review is requested, required by repository rules, or helps resolve a concrete remaining risk. SKILL.md owns when to review and when review ends.

Check the requested behavior, changed code, affected contracts and regressions. Use relevant verification evidence from the main thread or workers. A formal spec, task DAG, every kind of check, or a fresh test run by a particular role is not required.

Classify each finding:
- blocker: a demonstrated requirement violation, regression, security defect or mandatory repository-rule failure; give the location, triggering condition and expected behavior.
- missing-evidence: identify the specific missing check or result. Accept valid existing output when the relevant inputs are unchanged; otherwise request that check.
- suggestion: optional cleanup, style preference or speculative improvement; it does not block delivery.

Report whether concrete blockers or essential evidence gaps remain. A fundamental design defect should identify the violated contract or invariant, not merely propose a preferred architecture.

For follow-up, keep closed findings closed and inspect the repair plus its effects. Expand only if the repair changes contracts, critical invariants or risk boundaries. Do not create recurring full reviews for small corrections. In a read-only role, use supplied evidence and leave commands requiring workspace writes to the implementer.

