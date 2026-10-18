# Configuration synchronization

Requires Python 3.11+ with standard-library tomllib; no packages are needed. Run from the skill folder, or pass --root /path/to/polyforge.

## Repository check and synchronization

```text
python scripts/sync-config.py --check
python scripts/sync-config.py --sync-repo
```

--check is the default and writes nothing. It checks TOML syntax, all role bindings, offline model/effort support, model/effort/sandbox drift, route references, direct escalation chains, mandatory Astra design and follow-up role boundaries. SKILL and README versions must match the router.

--sync-repo updates only role name, model, model_reasoning_effort and sandbox_mode from the router, preserving descriptions, instructions and other content. All templates and destinations are validated before writes. Edit prose manually when behavior changes. Unknown models require a verified addition to model_support before use. The allowlist is a release snapshot; it does not check live account access or client support.

## Installation and backups

```text
python scripts/sync-config.py --install --dry-run
python scripts/sync-config.py --install
python scripts/sync-config.py --check-installed
```

Override CODEX_HOME / ~/.codex with --codex-home /path/to/codex when needed. Installation requires a passing repository check. It copies SKILL.md, README.md and files under agents, codex-agents, config, references, scripts and templates into skills/polyforge, then the eight bound role definitions into agents. Tests and caches are excluded. User config.toml and global defaults are untouched; unrelated roles are preserved. Only explicitly retired PolyForge role files are backed up and removed. The retired compatibility role is backed up and removed from its two known installation paths.

Changed existing files are backed up under polyforge-backups/<UTC timestamp>/ with paths relative to Codex home. New files need no backup; identical files are skipped. Containment checks run before writes. Symlinks escaping the intended destination are rejected. Restore individual files from backup as needed, then recheck. Repeated installation with unchanged sources writes nothing and creates no backup.

The retired `polyforge-luna56.toml` is removed only from `agents/` and `skills/polyforge/codex-agents/` beneath the selected Codex home, after both existing files have been backed up. --dry-run lists these deletions without performing them; --check-installed reports any retired file still present. Retirement entries cannot name an active role or escape these directories.

--check-installed compares both the installed package and managed roles to this release, without reading user config.toml or credentials. It is read-only. Installation to a restricted location remains subject to normal session permissions.

Start a new/reloaded session to expose changed roles. Choose GPT-6.1 Sol high for the main task separately; installation does not switch or hot-reload an active task.
