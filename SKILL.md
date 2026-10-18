---
name: polyforge
description: "Orchestrate coding requests through discovery, proportional model routing, safe implementation and verification. Use GPT-6.1 Sol high for orchestration, Luna max for bounded work, Astra high for initial major design, and GPT-6.1 Sol high for follow-up design and max for major complex implementation. Use for feature work, bug fixes, refactors and multi-step development; do not trigger for explanation or review-only requests unless implementation is requested."
metadata:
  version: "2.4.4"
  short-description: "Astra initial design, Sol follow-through and bounded Luna work"
---

# PolyForge

Turn a short user goal into a verified code delivery:

`goal → project context → targeted discovery → requirement expansion → ambiguity gate → light/standard/major flow → model routing → safe implementation → integration verification → conditional fresh review → context update → delivery`

## 0. Runtime configuration
Read `config/model-router.toml` at the start. It is the source for role bindings, model settings and routing gates. Custom agent TOML files are executable definitions, not automatically updated by reading the router. Run `python scripts/sync-config.py --check` from the skill folder when a Python 3.11+ runtime is available; use `--check-installed` when installation drift is relevant. Otherwise compare the selected role's model, effort and sandbox manually. Resolve relevant drift before spawning that role; missing or unavailable configuration must be disclosed, never silently replaced.

The main thread owns communication, approved requirements, task state, dependencies, spawning, integration, verification, project context and delivery. Its desired task/session setting is GPT-6.1 Sol high. The skill cannot switch the active thread or global defaults. If it differs, disclose the limitation and continue authorized work; do not claim a switch occurred.

Main orchestration and ordinary design use GPT-6.1 Sol high. Ordinary complex implementation and independent review retain GPT-6.1 Sol high. Initial major architecture and difficult rescue use Astra high. Major follow-up design uses GPT-6.1 Sol high and major complex implementation uses GPT-6.1 Sol max under an approved Astra baseline. Do not automatically raise any configured reasoning effort. Clear implementation remains with GPT-6 Luna max.

## 1. Project context and short-prompt understanding
If project context is enabled, locate the configured file (default `.polyforge/project-context.md`). If absent and auto-create is enabled, run the platform-appropriate initializer: `scripts/init-project-context.ps1` on PowerShell/Windows or `scripts/init-project-context.sh` on Bash/macOS/Linux/WSL. Load only entries relevant to the current task.

Context priority:
1. user instruction in this turn
2. durable user-confirmed decisions
3. current repository facts
4. older repo-verified project context
5. weak inference

Context is a cache, not truth. Verify material facts cheaply when possible. Never store secrets, credentials, raw chain-of-thought, temporary debug logs, or task-by-task history.

### Targeted discovery
Before deciding the workflow, gather only the context needed for this request. Prefer `polyforge-scout` for nontrivial discovery; the main thread may handle very small reads itself. Confirm relevant entry points, existing patterns, contracts/data models, tests/build/lint/typecheck commands, and applicable AGENTS.md/README instructions. Avoid broad scans without a reason.

### Requirement expansion
Create an internal `expanded_request` with:
- user_goal
- observed_context
- inferred_requirements
- assumptions
- hard_constraints
- success_criteria
- uncertainties
- context_used_and_verified

Preserve the user’s product scope. Do not invent adjacent features.

### Minimal-question ambiguity gate
Default to asking less:
- infer local implementation details from existing code and conventions when reliable;
- choose ordinary low-risk implementation details yourself;
- ask only when the unresolved choice materially changes product behavior, data model, public contract, core architecture, security boundary, or major compatibility behavior.

When a question is necessary, ask exactly one highest-impact question. After the answer, update the approved request and continue; do not restart analysis.

## 2. Choose light, standard, or major flow
Choose the cheapest flow covering the demonstrated risk. File counts and keywords are signals, not hard rules.

Micro-edit exception: the main thread may directly complete a tiny change only when scope is explicit, risk and blast radius are low, no material product or architecture decision is needed, no public contract/data/security/concurrency/migration behavior changes, and a quick observable check can verify it. Examples include a typo, a local display label or an isolated mechanical edit. Inspect the diff and run the appropriate check. If hidden complexity appears, stop using this exception and choose the appropriate flow. It does not permit the main thread to retain substantial bounded implementation merely because it has opened the files.

Light flow:
1. delegate bounded implementation to `default_worker`, unless the micro-edit exception applies;
2. wait for completion; elapsed time alone is not failure;
3. verify the acceptance criteria and inspect the diff;
4. deliver without a separate architect or reviewer when the evidence is sufficient.

Standard flow:
1. the GPT-6.1 Sol high orchestrator performs targeted discovery, ordinary design and bounded decomposition;
2. use GPT-6 Luna max for clear tasks; use GPT-6.1 Sol high for implementation that cannot safely be decomposed or for an evidence-based escalation;
3. integrate, inspect the full diff and run milestone/final verification;
4. deliver without a separate architect or reviewer unless the user or repository rules require one;
5. promote to major when material major-architecture criteria emerge.

Major flow:
1. the first major design must be performed by `architect_agent` (Astra high), even if the orchestrator believes it could design it itself;
2. confirm a concise `astra_design_baseline` containing the approved scope, design summary, contracts, critical invariants, risks, open decisions and verification plan;
3. assign clear implementation to GPT-6 Luna max; route non-decomposable major complex implementation and relevant escalations to `major_complex_worker` (GPT-6.1 Sol max);
4. for subsequent local design changes within that baseline, use `followup_architect_agent` (GPT-6.1 Sol high, read-only); do not rerun the full initial design unnecessarily;
5. integrate, verify and obtain a fresh GPT-6.1 Sol high review;
6. repair concrete findings and rerun affected checks; rereview when changes materially affect the verdict.

Major follow-up roles require an actual confirmed Astra baseline. A task is not a follow-up merely because the user says "change it again". A new major goal, fundamental design replacement, critical invariant/security boundary/migration strategy change, or evidence invalidating the baseline requires a new Astra design pass. Preserve the existing Astra invocation gate: a second invocation in the same task needs materially new evidence and a recorded reason.

## 3. Major-architecture design
Ordinary design remains with the orchestrator. Major design is demonstrated by at least one material condition:
- irreversible or high-risk migration;
- cross-service public-contract change;
- permission, authentication or critical security-boundary change;
- distributed consistency, transactions or difficult concurrency;
- replacement of a core architecture across modules;
- material design uncertainty unresolved by the orchestrator's repository evidence.

The first design for each major scope must use Astra high. Pass the approved expanded request and relevant evidence to the read-only architect. After confirmation, carry the concise `astra_design_baseline` through handoffs; it contains reviewable facts and decisions, not hidden reasoning. A prior successful baseline may be reused only after verifying its relevance against current repository facts and user requirements.

Use the read-only GPT-6.1 Sol high refiner for local follow-up changes preserving the approved critical boundaries and invariants. Require a `design_delta`, preserved invariants, affected tasks and verification changes. Missing baseline returns to initial Astra design. Fundamental redesign returns to Astra, with the real new evidence; permission/dependency problems do not justify model escalation.

Require a task DAG. Every task must include:
`task_id, goal, depends_on, in_scope_files_or_systems, forbidden_changes, interface_contracts, acceptance_criteria, verification_commands, complexity, complexity_reason, parallel_safe, conflict_scope, open_decisions`.

If a material user decision is missing, ask the highest-impact question and continue independent work. Otherwise proceed automatically.

## 4. Model routing
Main orchestrator and ordinary design = GPT-6.1 Sol high. Initial major architect = Astra high. Default worker = GPT-6 Luna max. Ordinary complex worker = GPT-6.1 Sol high. Major follow-up designer = GPT-6.1 Sol high. Major complex worker = GPT-6.1 Sol max. Fresh major reviewer = GPT-6.1 Sol high. Difficult rescue = Astra high.

Route individual tasks by scope, coupling, unknowns, blast radius, contracts, security/concurrency/migration risk and debugging evidence. Clarify contracts and split safely before choosing a stronger implementation worker. Clear implementation, including clear portions of major work, remains with Luna. Record the concrete non-decomposable risk or failure evidence before selecting Sol or Astra. After resolving a difficult scope, return bounded remaining implementation to Luna.

The main thread may edit production code for the micro-edit exception or a concrete integration/contract conflict. Record why integration work cannot cleanly be delegated. Other bounded production changes, tests and task-specific documentation belong to workers. Workers are not alone in the workspace: preserve other agents' valid edits and stay within the assigned write scope.

## 5. Safe delegation and parallelism
Delegate independent tasks to subagents when useful. Parallel writes are allowed only when all are true:
- `parallel_safe = true`;
- dependencies are satisfied;
- write/conflict scopes do not overlap;
- tasks do not compete on migrations, generated artifacts, global state, or other shared mutable resources.

Never exceed `max_parallel_workers`. If Codex/session concurrency is lower or a spawn fails because capacity is exhausted, queue the remaining work serially rather than treating the task as failed. Wait for requested agents to finish before integrating dependent work.

## 6. Self-repair, escalation, and difficult rescue
Do not interrupt, duplicate or upgrade a worker merely because it has run a long time. If the platform or user interrupts work, preserve available state and resume from the handoff.

Grade difficult work by evidence without adding mandatory rescue roles. A local implementation failure stays with the current worker for its focused repair; cross-module or unknown-root-cause failures use the appropriate Sol worker; unresolved fundamental design or demonstrated capability failures use Astra. Permission, dependency and missing user-decision blockers are resolved directly rather than passed through stronger models. These are routing decisions, not a requirement to run every level.

Default escalation: GPT-6 Luna → GPT-6.1 Sol high → Astra high. For major complex work under an approved Astra baseline, use GPT-6.1 Sol max in place of Sol high; do not add high then max as two mandatory steps.

When a Luna worker fails acceptance, return actual failure evidence to that same worker for the configured self-repair attempt (default one). If still failing, continue from existing work with the appropriate Sol worker. Skip Luna when new evidence already establishes non-decomposable/high-risk implementation; do not force a predictable failure first. No intermediate worker tier is inserted automatically.

The selected Sol worker gets one focused evidence-based self-repair attempt. If that still fails, progress demonstrably stalls or the scope exceeds its capability, send only the smallest difficult scope to Astra high. Ordinary specification gaps return to the orchestrator; local major design gaps go to the high refiner; fundamental major design errors return to Astra. Missing permissions, dependencies or required user decisions are blockers, not capability failures.

Use `references/handoff.md` for every implementation escalation or return to Luna, including current_state, completed_work, changed_files, remaining_work, failure_evidence and verification_history; include the Astra baseline for major follow-up roles. Continue from existing correct work instead of restarting or bouncing between workers.

Allow at most one automatic Astra invocation per task. A second invocation requires materially new evidence and an explicit reason recorded by the orchestrator. Initial major design already counts; later rescue or fundamental redesign needs that new evidence. Astra reports unresolved blockers instead of starting an endless retry cycle.

## 7. Integration and verification
Implementation workers run focused checks for their assigned scope and return the commands, results, and concise failure evidence. After dependent work is integrated, the orchestrator:
- checks the full diff and unexpected changes;
- verifies every acceptance criterion and contract consistency across tasks;
- runs required integration and full test/build/lint/typecheck checks at the milestone or final delivery, and repeats affected checks after material changes; do not rerun the full suite after every worker solely to duplicate a passing focused check;
- records actual evidence, never claimed evidence.

If verification fails, route the concrete evidence back to the responsible worker; do not rewrite the entire task by default.

## 8. Fresh final review
For major flow, spawn a new configured GPT-6.1 Sol high reviewer (normally `polyforge-reviewer`) only after integration verification. Provide the original approved requirements, relevant code context, full diff, and actual verification evidence. Missing evidence means fix-first, not an automatic reasoning-effort increase. Light and standard flows skip the separate reviewer unless the user or applicable repository rules explicitly require one.

- `ship` → deliver.
- `fix-first` → route concrete findings to the best worker, re-verify, then use a fresh review again.
- `rethink` → use the high refiner for a local baseline-preserving design correction; return to Astra for fundamental redesign, with new evidence and a recorded reason. Rerun only affected tasks.

Reviewer does not edit source or run checks that write to the workspace. Workers run focused writable checks for their scope; the orchestrator runs required integration and final checks.

## 9. Durable project-context update
Only after successful light or standard verification, or a major-flow `ship`, update project context. The orchestrator is the single writer.

Store only durable facts: user-confirmed decisions, repo-verified architecture/contracts, stable commands, reusable conventions. Validate worker `context_candidates` before promoting them. Mark superseded facts stale. If nothing durable changed, do not write anything.

For a long release, close work at reviewable milestones and keep the durable context current. When the user chooses to continue in a fresh task, use that context plus a concise verified handoff instead of replaying the old task's logs. Do not create or move a task solely because a milestone ended.

## 10. Final delivery
Report concisely:
- what was delivered;
- key implementation/design outcomes;
- verification evidence;
- remaining risks or unfinished items, if any.

Do not calculate or report dollar/token cost unless the user explicitly asks. PolyForge normally optimizes model use through routing, not through cost accounting.

## 11. Operational notes
- Invoke with `$polyforge ...` or select it with `/skills`.
- For installation, synchronization, offline validation and backup behavior, read `references/configuration.md`. The sync script installs the skill and eight managed role files without changing user `config.toml`, global defaults or unrelated roles. It does not check live account model access or client support.
- Newly installed or changed roles must be exposed by a new/reloaded session before use. Do not assume hot reload. If a selected role is missing, use a general agent with the exact model, effort and sandbox only when the session supports it; otherwise disclose the limitation. Never substitute Sol high for the configured max implementation role silently.
- Preserve parent permission boundaries and report the real permission error.
- Codex behavior is authoritative; Claude Code compatibility remains a secondary extension surface.
