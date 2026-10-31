# PolyForge

PolyForge v3.2.0 prioritizes completing the user's development requirements with a short loop:

`understand → implement → verify affected behavior → deliver`

The main thread implements ordinary features, fixes, refactors, tests and documentation directly. Delegation helps when independent parallel work or a specialist will save time. Routine development does not require a task DAG, an architecture pass, repeated approvals or an independent reviewer.

Verification follows the change: use focused checks, reuse still-valid results, and expand to integration or full-suite checks when the impact or repository rules require them. Review findings distinguish real defects, missing evidence and optional suggestions. After a repair, the existing reviewer checks the affected scope rather than starting a fresh full review.

## Model routing

Choose assistance by the actual work. The main task remains Sol high; seven optional helpers cover focused discovery, bounded work, difficult implementation, design, review and rescue.

| Optional role | Model and reasoning |
| --- | --- |
| Main task preference | GPT-6.1 Sol `high` |
| Repository scout | GPT-6 Luna `high` |
| Bounded implementation helper | GPT-6 Luna `max` |
| Regular features and moderately difficult scoped fixes | GPT-6.1 Terra `max` |
| Complex implementation helper | GPT-6.1 Sol `xhigh` |
| Independent reviewer | GPT-6.1 Sol `high` |
| Read-only architecture consultant | GPT-6 Astra `xhigh` |
| Difficult implementation rescue | GPT-6 Astra `xhigh` |

Ordinary work stays in the main thread. Simple or repetitive independent tasks can use Luna max. Regular features, known-pattern business logic, several-file changes and moderately difficult scoped fixes can use Terra max when the approach, contracts and checks are clear; screenshot-driven UI adjustments are another suitable bounded assignment. Sol xhigh is reserved for tightly coupled cross-module changes, concurrency/transactions, difficult bugs and contract-heavy refactors. Astra xhigh handles consequential unresolved design questions or difficult implementation rescue; its read-only and writable roles remain separate.

Select a suitable helper directly without traversing a fixed model ladder. Terra is an optional task-based choice, not a mandatory escalation step. Existing workable designs need no preliminary Astra pass or named baseline. The current owner can finish the remaining work without a forced return to Luna. Local design refinement stays with the main thread, and the old major worker is merged into the complex helper. The skill cannot switch the active main-thread model or silently change a configured role's effort.

## Install or update

Use Python 3.11+; no third-party packages are needed. From this repository or an unpacked release:

```text
python scripts/sync-config.py --install
```

Installation validates the package, copies the skill and seven managed roles, and backs up changed existing files. On upgrade, retired PolyForge refiner and major-worker role files are backed up before removal. It preserves user config.toml, global defaults and unrelated roles. Unchanged installations write nothing.

Start a new/reloaded Codex session after updating so old skill and role instructions are replaced, then invoke `$polyforge`. Ordinary development does not require running an installation check before each task.

For package maintenance:

```text
python scripts/sync-config.py --check
python scripts/sync-config.py --install --dry-run
python scripts/sync-config.py --check-installed
```

After editing model settings in config/model-router.toml, run `python scripts/sync-config.py --sync-repo` and install. The checker validates configuration and installation consistency, not live model access or the quality of workflow decisions. See [configuration and backups](references/configuration.md).

Existing project context may be used when helpful. The initializers under scripts/ are optional utilities, not a development prerequisite.

