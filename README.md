# PolyForge

PolyForge v2.4.3 takes coding requests from targeted discovery through implementation and verification. Light, standard and major workflows keep model use proportional to risk. Clear, low-risk micro edits with quick observable verification may be completed by the main thread.

| Role | Model and reasoning |
| --- | --- |
| Main orchestrator and ordinary design | GPT-6.1 Sol `max` |
| Repository scout | GPT-6 Luna `medium` |
| Default bounded implementation | GPT-6 Luna `max` |
| Ordinary complex implementation | GPT-6.1 Sol `high` |
| Independent major-flow review | GPT-6.1 Sol `high` |
| First major design | GPT-6 Astra `high`, required |
| Local follow-up major design | GPT-6.1 Sol `max`, read-only |
| Major complex implementation after Astra design | GPT-6.1 Sol `max`, workspace-write |
| Difficult rescue / fundamental major redesign | GPT-6 Astra `high` |

Clear implementation remains with Luna even in major work. The two new max roles require a confirmed Astra design baseline and cannot replace the first design. A new major scope or fundamental change to critical invariants returns to Astra.

Default escalation is Luna → one evidence-based self-repair → Sol → one focused self-repair → Astra for the smallest difficult scope. Ordinary complex implementation uses Sol high; major complex work with an Astra baseline uses Sol max. Time alone is not a failure.

## Check and install

Use Python 3.11+; no third-party packages are required. From this repository or the unpacked release folder:

```text
python scripts/sync-config.py --check
python scripts/sync-config.py --install --dry-run
python scripts/sync-config.py --install
python scripts/sync-config.py --check-installed
```

Installation copies the skill into `$CODEX_HOME/skills/polyforge` and eight managed roles into `$CODEX_HOME/agents`, using `~/.codex` when CODEX_HOME is unset. Changed existing files are backed up. User config.toml, global defaults and unrelated agents are preserved. Retired PolyForge role files are backed up before removal. No installation occurs unless --install is supplied.

Start a new/reloaded Codex session after installing roles. Choose GPT-6.1 Sol max for the main task, then invoke `$polyforge`. The skill cannot switch the active main-thread model, and installing files does not hot-reload exposed roles.

After editing config/model-router.toml, run `python scripts/sync-config.py --sync-repo`, review role-file changes and install. Descriptions and developer instructions remain hand-authored and must stay semantically consistent. Offline validation does not prove live account access or client support.

See [configuration and backups](references/configuration.md). Project-context initializers remain under scripts/init-project-context.ps1 and scripts/init-project-context.sh and run from the target project.
