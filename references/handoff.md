# PolyForge structured handoff

Use for every implementation delegation and escalation (GPT-6 Luna → GPT-5.6 Luna → Sol complex worker → Astra), and for returning bounded work to a Luna worker. Skip a tier when the routing evidence warrants it.

```yaml
task_id: T1
goal: "Exact deliverable"
user_goal: "Original user goal"
assumptions: []
relevant_project_context: []

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
