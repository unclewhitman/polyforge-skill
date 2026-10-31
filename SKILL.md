---
name: polyforge
description: "Use when implementing features, bug fixes, refactors or multi-step development from a user's requirements. Not for explanation-only or review-only requests."
metadata:
  version: "3.2.0"
  short-description: "Direct implementation with focused verification"
---

# PolyForge

Complete the requested development efficiently. Default to main-thread implementation and a short loop:

`understand the requirement → implement → verify what changed → deliver`

## Implement directly

Read the relevant code, applicable repository instructions and existing examples. Once the behavior and acceptance conditions are clear, start implementing. Choose ordinary implementation details from repository conventions. Ask only when a missing decision prevents correct implementation or materially changes the user's intended scope.

The main thread can implement features, fixes, refactors, tests and documentation. Routine work needs no workflow classification, formal expanded request, task DAG, separate design document or intermediate approval. Use a brief plan only when it helps manage dependencies. Improve the requested behavior without adding adjacent features or speculative refactors.

Use existing project context when it saves discovery. Verify material facts against current code. Creating context files and running configuration checks are not prerequisites for development; update context only when a useful durable decision or fact changes.

## Use assistance when it saves time

Delegate a bounded independent task when parallel work or specialized help will reduce completion time. Otherwise keep the work in the current thread. Give the helper the goal, relevant files or boundaries, and how to verify success; use a full handoff only when changing owners or escalating stalled work. Continue with the same worker for local corrections.

Model bindings and reasoning efforts are defined in `config/model-router.toml`. Read it when selecting a configured helper, not as a per-task setup ceremony. The main-task preference is Sol high; the skill does not change the active main-thread model. If an optional role is unavailable, continue work the current session can safely perform and report only the limitation that matters.

Select assistance by the actual work:
- scout: Luna high, read-only, for a targeted repository question;
- bounded worker: Luna max, for simple, repetitive, clearly bounded independent implementation;
- implementation worker: GPT-6.1 Terra max, for regular features and moderately difficult scoped fixes with an existing approach, clear contracts and observable checks;
- complex worker: Sol xhigh, for tightly coupled cross-module changes, difficult debugging, concurrency, transactions or contract-heavy refactors;
- architect: Astra xhigh, read-only, for a consequential unresolved design question;
- rescue worker: Astra xhigh, workspace-write, for a difficult root cause or implementation beyond the current worker's capability;
- reviewer: Sol high, read-only, for the optional independent review described below.

These are alternatives, not a mandatory ladder. Choose a suitable helper directly when evidence supports it; prior failure in a weaker model is not required. For delegated work, choose Luna max for simple or repetitive changes, Terra max for known-pattern business logic, several-file feature changes or scoped fixes with clear contracts and checks, and Sol xhigh for tightly coupled work or difficult unknowns. Terra can also handle scoped screenshot-driven UI adjustments with observable verification. Choose Terra directly when it fits; neither a Luna failure nor a Terra pass is required before choosing another helper. An existing workable design is enough to implement, including complex work: no Astra pass or named design baseline is required. The main thread handles local design refinements. After a difficult part is resolved, the current owner can finish the remaining work instead of handing it back merely to use a smaller model. Read role instructions only when using that role.

Keep concurrent write scopes independent and respect the session's capacity. Preserve other contributors' valid changes. On failure, repair the affected scope using concrete evidence; repeated failure on the same cause calls for diagnosis or a better-suited helper rather than restarting correct work or cycling through every model. Permissions, dependencies and missing user decisions are resolved directly; they are not reasons to increase model effort.

## Verify proportionally

Choose the smallest checks that demonstrate the requested behavior and cover the affected risks. A focused test, build, typecheck, lint check or manual inspection may be sufficient depending on the change. Add tests when they protect changed behavior; simple copy or mechanical edits can use a direct observable check.

Run broader integration or full-suite checks when dependencies, shared code, contracts or repository requirements make them necessary. The main thread owns the adequacy of verification and can use valid worker evidence. Reuse passing results while the relevant code, dependencies, configuration and environment remain unchanged. After a local repair, rerun the affected checks; expand only when the repair affects a broader scope.

Report actual commands and results, including meaningful gaps. Evidence missing from a summary can be supplied from an existing valid run; a genuinely missing check needs that check, not a code-repair task.

## Review only when useful

Inspect the diff and acceptance conditions before delivery. Independent review is optional, including for large work: use it when requested, required by repository rules, or needed to resolve a concrete remaining risk. Read `references/review-checklist.md` only when performing that review.

Only a demonstrated requirement violation, regression, security defect or mandatory repository-rule failure blocks delivery. Keep optional cleanup, style preferences and hypothetical improvements as suggestions.

When independent review is used, start with one independent pass. Return corrections to the original worker or fix them in the main thread. The same reviewer can check the repair and close the existing findings; reopen broader review only when the repair changes a contract, critical invariant or risk boundary. Newly discovered concrete blocking defects still need resolution.

Distinguish code defects, missing evidence and suggestions. Supply valid existing evidence directly. Stop adding review rounds when blocking findings are closed and the necessary checks pass; do not restart a fresh full review for each small correction.

## Deliver

Summarize what changed, the verification performed, and any material unfinished item. Once the requested behavior is implemented and the necessary checks pass, deliver. Further polish follows the user's next request.

For installation or configuration drift, read `references/configuration.md`. For a real ownership change, see `references/handoff.md`. Keep permission boundaries, user data and truthful verification intact.

