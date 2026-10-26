# PolyForge

PolyForge v3.0.0 prioritizes completing the user's development requirements with a short loop:

`understand → implement → verify affected behavior → deliver`

The main thread implements ordinary features, fixes, refactors, tests and documentation directly. Delegation helps when independent parallel work or a specialist will save time. Routine development does not require a task DAG, an architecture pass, repeated approvals or an independent reviewer.

Verification follows the change: use focused checks, reuse still-valid results, and expand to integration or full-suite checks when the impact or repository rules require them. Review findings distinguish real defects, missing evidence and optional suggestions. After a repair, the existing reviewer checks the affected scope rather than starting a fresh full review.

## Model routing

This release keeps the v2.4.4 model bindings, reasoning efforts and escalation order unchanged. Model-routing changes are separate from this workflow simplification.

| Optional role | Model and reasoning |
| --- | --- |
| Main task preference | GPT-6.1 Sol `high` |
| Repository scout | GPT-6 Luna `medium` |
| Bounded implementation helper | GPT-6 Luna `max` |
| Ordinary complex helper | GPT-6.1 Sol `high` |
| Independent reviewer | GPT-6.1 Sol `high` |
| Initial major design | GPT-6 Astra `high` |
| Follow-up major design under an Astra baseline | GPT-6.1 Sol `high` |
| Major complex implementation under an Astra baseline | GPT-6.1 Sol `max` |
| Difficult rescue | GPT-6 Astra `high` |

When helpers are needed, existing escalation remains Luna → Sol → Astra, preserving correct work and real failure evidence. A genuine major-architecture design still uses the Astra-first baseline and existing follow-up role boundaries. These roles are available tools, not a required sequence for every request. The skill cannot switch the active main-thread model.

## Install or update

Use Python 3.11+; no third-party packages are needed. From this repository or an unpacked release:

```text
python scripts/sync-config.py --install
```

Installation validates the package, copies the skill and eight managed roles, and backs up changed existing files. It preserves user config.toml, global defaults and unrelated roles. Unchanged installations write nothing.

Start a new/reloaded Codex session after updating so old skill and role instructions are replaced, then invoke `$polyforge`. Ordinary development does not require running an installation check before each task.

For package maintenance:

```text
python scripts/sync-config.py --check
python scripts/sync-config.py --install --dry-run
python scripts/sync-config.py --check-installed
```

After editing model settings in config/model-router.toml, run `python scripts/sync-config.py --sync-repo` and install. The checker validates configuration and installation consistency, not live model access or the quality of workflow decisions. See [configuration and backups](references/configuration.md).

Existing project context may be used when helpful. The initializers under scripts/ are optional utilities, not a development prerequisite.

