# PolyForge structured handoff

Use for every implementation delegation and escalation (GPT-6 Luna → GPT-6.1 Sol high → Astra high; major complex work with an Astra baseline uses GPT-6.1 Sol max instead of high), and for returning bounded work to Luna.

```yaml
task_id: T1
goal: "Exact deliverable"
user_goal: "Original user goal"
assumptions: []
relevant_project_context: []
workflow_level: standard # light | standard | major
astra_design_baseline: null # required for major follow-up design / complex implementation
design_delta: []

depends_on: []
parallel_safe: true
conflict_scope: []

scope:
  in_scope: []
  forbidden: []

contracts: []
acceptance: []
verification_commands: []

current_state:
  status: not_started   # not_started | in_progress | stalled | failed | completed
  changed_files: []
  completed_work: []
  remaining_work: []
  failure_evidence: []
  verification_history: []

context_candidates: []
open_decisions: []
```

Parallel work is allowed only when dependencies are satisfied and write/conflict scopes do not overlap. Workers never write project context directly.
