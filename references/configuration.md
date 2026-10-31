# Configuration and installation

Use Python 3.11+ with standard-library tomllib. Run from the skill folder or pass --root /path/to/polyforge. These are package-maintenance commands, not per-task development gates.

## Install or update

```text
python scripts/sync-config.py --install
```

Installation first validates the package, then copies the skill and seven managed role definitions under CODEX_HOME (default ~/.codex). It preserves user config.toml, global defaults and unrelated roles. Start a new/reloaded session to expose updated instructions; installation cannot change the active main-thread model or hot-reload roles.

To preview or diagnose an installation:

```text
python scripts/sync-config.py --install --dry-run
python scripts/sync-config.py --check-installed
```

Changed existing files are backed up under polyforge-backups/<UTC timestamp>/ before replacement. Identical files are skipped. Only named retired PolyForge roles are backed up and removed from their known installation paths. Restore individual files from backup if needed. Containment checks reject writes through redirected destinations or outside the intended directory.

Retired roles are polyforge-luna56.toml, polyforge-refiner.toml and polyforge-major-worker.toml. Their known paths are agents/<filename> and skills/polyforge/codex-agents/<filename> beneath the selected CODEX_HOME. Upgrade backs up both locations before removing them; --dry-run previews the changes and --check-installed reports retired files left behind.

## Maintain the package

```text
python scripts/sync-config.py --check
python scripts/sync-config.py --sync-repo
```

--check validates TOML, role bindings, supported offline model/effort combinations, managed-header drift, read/write role boundaries and release versions. Model and effort settings come from the router; the checker does not enforce particular model identities, an escalation ladder or an Astra design prerequisite.

--sync-repo updates role name, model, model_reasoning_effort and sandbox_mode while preserving descriptions and developer_instructions. Keep behavior in SKILL.md and align role text when changing responsibilities; passing configuration checks does not prove behavioral consistency or live account/model availability.

Workflow guidance is defined in SKILL.md. Role model settings and helper bindings are in config/model-router.toml. Select a helper by task needs; all implementation helpers can start from an existing workable design. Main-thread implementation is allowed for the user's authorized development scope.

Optional project-context initializers run from the target project. Existing context is a cache of durable facts, not an approval gate or mandatory artifact.

