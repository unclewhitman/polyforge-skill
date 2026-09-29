---
name: polyforge
description: "Orchestrate end-to-end coding from short or underspecified requests with cost-aware routing: GPT-6 Sol high for orchestration, GPT-6 Luna max for routine implementation, GPT-5.6 Luna max for bounded moderate implementation, GPT-6 Sol high for complex implementation and review, and Astra medium for major architecture and difficult rescue. Use for feature work, bug fixes, refactors, and multi-step development where the user wants Codex to manage the workflow. Do not trigger for pure explanations or review-only questions unless implementation is requested."
metadata:
  version: "2.3.0"
  short-description: "Cost-aware coding orchestration with Luna-first implementation"
---

# PolyForge

Turn a short user goal into a verified code delivery:

`goal → project context → targeted discovery → requirement expansion → ambiguity gate → light/standard/major flow → model routing → safe implementation → integration verification → conditional fresh review → context update → delivery`

## 0. Runtime configuration
Read `config/model-router.toml` at the start. It is the runtime source for agent names, behavior switches, thresholds, and routing signals. If missing, continue only with conservative defaults and tell the user to reinstall PolyForge; never silently assume stale settings.

The main thread is the orchestrator. It owns user communication, approved requirements, task state, dependencies, agent spawning, integration, verification, context updates, and final delivery. Keep noisy exploration/logs in subagents where useful.

The desired main-thread setting is GPT-6 Sol high. This is a task/session setting, not an automatic model switch: do not change global defaults or claim the active thread was switched by reading this skill. If the active setting differs, disclose the limitation and continue authorized work.

The orchestrator handles ordinary design and decomposition itself. Astra medium is reserved for major architecture and last-resort rescue. Independent review uses GPT-6 Sol high. Do not automatically raise any configured reasoning effort.

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
Choose the cheapest flow that covers the demonstrated risk. File-count thresholds and keywords are signals, not hard rules.

Light flow:
1. delegate implementation to `default_worker` (normally `polyforge-luna`);
2. wait for completion; elapsed time alone is not failure;
3. run relevant verification and inspect diff;
4. if verified, deliver without architect or reviewer;
5. if hidden complexity appears, promote only as far as necessary.

Use light flow only when scope is clear, blast radius and risk are low, no material architecture or product decision is needed, and completion can be mechanically verified.

Standard flow:
1. the GPT-6 Sol high orchestrator performs targeted discovery, ordinary design, and bounded task decomposition;
2. assign routine bounded implementation, focused tests, and task-specific documentation to GPT-6 Luna max; use GPT-5.6 Luna max for moderately difficult but well-bounded work, and GPT-6 Sol high only for portions that cannot be safely decomposed;
3. integrate, inspect the full diff, and run integration or final verification as described in section 7;
4. deliver without a separate architect or reviewer when the evidence is sufficient;
5. promote to major flow only when major-architecture criteria emerge.

Use standard flow for substantive or multi-step work whose interfaces and risks can be resolved by the orchestrator without a separate major-architecture pass.

Major flow:
1. spawn the configured Astra medium architect for a bounded design pass;
2. implement the resulting task DAG with GPT-6 Luna max by default, GPT-5.6 Luna max for moderately difficult bounded tasks, and GPT-6 Sol high where necessary;
3. integrate and verify in the main thread;
4. spawn a fresh GPT-6 Sol high reviewer;
5. repair concrete findings, re-verify, and repeat review with a fresh reviewer only when changes materially affect the verdict.

## 3. Major-architecture design
Ordinary design remains with the orchestrator. Spawn the configured architect (normally `polyforge-architect`) only when at least one material condition is demonstrated:
- irreversible or high-risk data migration;
- a cross-service public-contract change;
- a permission, authentication, or critical security-boundary change;
- distributed consistency, transaction, or difficult concurrency design;
- replacement of a core architecture across multiple modules;
- a major design uncertainty that the Sol orchestrator cannot resolve from repository evidence.

Pass the Astra medium architect the approved expanded request and only relevant repository/context evidence. Keep it read-only and require a bounded design result rather than implementation.

Require a task DAG. Every task must include:
`task_id, goal, depends_on, in_scope_files_or_systems, forbidden_changes, interface_contracts, acceptance_criteria, verification_commands, complexity, complexity_reason, parallel_safe, conflict_scope, open_decisions`.

If architect reports a material open decision, the orchestrator asks the user one question at a time. Otherwise continue automatically.

## 4. Model routing
Main orchestrator and ordinary designer = GPT-6 Sol high. Major architect = Astra medium. Default worker = GPT-6 Luna max. Moderate worker = GPT-5.6 Luna max. Complex worker = GPT-6 Sol high. Independent major-flow reviewer = GPT-6 Sol high in a fresh instance. Difficult rescue worker = Astra medium.

Prefer Luna for every implementation task whose scope, contracts, and acceptance criteria are clear. Use `default_worker` (`polyforge-luna`, GPT-6 Luna max) for routine or narrowly focused work. Use `moderate_worker` (`polyforge-luna56`, GPT-5.6 Luna max) directly when the task has several interacting components or nontrivial logic but its interfaces, risks, and acceptance checks are already clear. Do not use file count or keywords alone to make this choice. Architectural complexity alone does not require a stronger implementation worker: clarify and split the design, then assign bounded tasks to the appropriate Luna tier. Route individual tasks, not entire projects. Reserve the Sol high complex worker for high-coupling implementation that cannot be safely decomposed; keep independent straightforward portions with GPT-6 Luna. After Astra resolves a major design or difficult root cause, return remaining bounded implementation to a suitable Luna worker.

The orchestrator owns design, task boundaries, cross-task integration, and final acceptance. Do not retain bounded production changes, test repairs, or task-specific documentation in the main thread merely because it is already inspecting those files; delegate them to Luna. The orchestrator may edit production code to resolve a concrete integration or contract conflict, and records why that work cannot be handed off cleanly. Before assigning implementation to Sol or Astra, record the specific non-decomposable risk or failure evidence; return clear remaining work to Luna.

Do not route by keyword alone. Use actual scope, coupling, unknowns, blast radius, public-contract/data-model impact, security/concurrency/migration risk, and debugging difficulty. The router’s `complexity_escalators` are signals only.

## 5. Safe delegation and parallelism
Delegate independent tasks to subagents when useful. Parallel writes are allowed only when all are true:
- `parallel_safe = true`;
- dependencies are satisfied;
- write/conflict scopes do not overlap;
- tasks do not compete on migrations, generated artifacts, global state, or other shared mutable resources.

Never exceed `max_parallel_workers`. If Codex/session concurrency is lower or a spawn fails because capacity is exhausted, queue the remaining work serially rather than treating the task as failed. Wait for requested agents to finish before integrating dependent work.

## 6. Self-repair, escalation, and difficult rescue
PolyForge imposes no time-based Luna cutoff. Do not interrupt, duplicate, or upgrade either Luna worker merely because it has run a long time. Platform/user interruptions can still happen; if one occurs, preserve available state and resume from the handoff instead of assuming failure.

If either Luna worker fails acceptance:
1. return the actual failure evidence to the same worker;
2. allow the configured self-repair attempts (default 1);
3. if GPT-6 Luna still fails on a bounded task, hand off once to GPT-5.6 Luna max; if GPT-5.6 Luna still fails, escalate to the Sol high complex worker. Skip the intermediate tier only when new evidence shows the task is high-risk, cannot be safely decomposed, or the failure is a specification/architecture issue. Do not restart a failed task from scratch or bounce it between Luna workers.

On every implementation escalation or return to Luna, send the structured handoff from `references/handoff.md`, including current_state, completed_work, changed_files, remaining_work, failure_evidence, and verification_history. The receiving worker continues from existing work unless evidence proves the direction is wrong.

For complex-worker implementation failures, first return concrete evidence for one focused self-repair attempt. If repair still fails, effective progress stalls, or the task demonstrably exceeds its boundary, route only the smallest difficult scope to Astra medium. Do not escalate merely because of elapsed time. Specification or architecture errors return to the architect when major-flow criteria apply; otherwise the orchestrator revises the ordinary design. Unavailable permissions, dependencies, or required user decisions are blockers to resolve, not model-capability failures.

Allow at most one automatic Astra invocation per task. A second Astra invocation requires materially new evidence and an explicit reason recorded by the orchestrator. If Astra was already used for major architecture, later rescue therefore needs new failure evidence. Astra reports unresolved blockers honestly instead of starting an endless retry cycle.

## 7. Integration and verification
Implementation workers run focused checks for their assigned scope and return the commands, results, and concise failure evidence. After dependent work is integrated, the orchestrator:
- checks the full diff and unexpected changes;
- verifies every acceptance criterion and contract consistency across tasks;
- runs required integration and full test/build/lint/typecheck checks at the milestone or final delivery, and repeats affected checks after material changes; do not rerun the full suite after every worker solely to duplicate a passing focused check;
- records actual evidence, never claimed evidence.

If verification fails, route the concrete evidence back to the responsible worker; do not rewrite the entire task by default.

## 8. Fresh final review
For major flow, spawn a new configured GPT-6 Sol high reviewer (normally `polyforge-reviewer`) only after integration verification. Provide the original approved requirements, relevant code context, full diff, and actual verification evidence. Missing evidence means fix-first, not an automatic reasoning-effort increase. Light and standard flows skip the separate reviewer unless the user or applicable repository rules explicitly require one.

- `ship` → deliver.
- `fix-first` → route concrete findings to the best worker, re-verify, then use a fresh review again.
- `rethink` → return to architect and rerun only affected tasks.

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

Do not calculate or report dollar/token cost. PolyForge optimizes model use through routing, not through cost accounting.

## 11. Operational notes
- Explicit invocation in Codex: `$polyforge ...` (or select it with `/skills`).
- Custom agents are expected under `~/.codex/agents/`; keep their model settings synchronized with `config/model-router.toml`, including both Luna workers, the Astra major architect, Sol complex worker and reviewer, and Astra rescue worker. Newly added or changed roles must be exposed by the session before use; if unavailable, use an explicitly configured general agent when supported, or disclose the limitation. Do not assume an already-loaded custom role has hot-reloaded.
- Subagent permission behavior is still bounded by the parent Codex session. If a required action is denied, surface the real permission error rather than pretending the task failed logically.
- Claude Code compatibility is retained as a secondary extension surface; Codex behavior is authoritative in this release.
