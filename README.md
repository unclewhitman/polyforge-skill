# PolyForge

PolyForge v2.1.0 is a Codex skill for taking a coding request from repository discovery through implementation and verification. It uses light, standard, and major workflows to keep model use proportional to the task.

| Role | Model and reasoning |
| --- | --- |
| Main orchestrator and ordinary design | GPT-6 Sol `xhigh` |
| Repository scout | GPT-6 Luna `medium` |
| Default implementation | GPT-6 Luna `max` |
| Complex implementation | GPT-6 Sol `high` |
| Independent major-flow review | GPT-6 Sol `high` |
| Major architecture and last-resort rescue | GPT-6 Astra `medium` |

## Install in Codex

1. Clone this repository into `~/.codex/skills/polyforge` (or `$CODEX_HOME/skills/polyforge` if `CODEX_HOME` is set).
2. Copy the six TOML files from `codex-agents/` into `~/.codex/agents/` (or `$CODEX_HOME/agents/`). They are custom agent definitions; keeping them only inside the skill directory does not register those roles.
3. Start a new Codex task using GPT-6 Sol with `xhigh` reasoning and invoke `$polyforge`. The skill cannot change the main task's model itself. Restart or reload Codex after installing or updating custom agents.

`config/model-router.toml` records the role settings and routing gates. Keep it synchronized with the installed custom agent TOML files. PolyForge normally assigns bounded implementation to Luna, uses Astra only for demonstrated major architecture or difficult rescue, and caps automatic Astra use at one invocation per task.

The `scripts/init-project-context.ps1` and `scripts/init-project-context.sh` helpers create a project-local context file when the skill needs one. They are run from the target project, not from this repository.
