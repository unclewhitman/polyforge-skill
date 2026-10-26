#!/usr/bin/env python3
"""Validate, synchronize and explicitly install PolyForge (Python 3.11+)."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
try:
    import tomllib
except ImportError:
    raise SystemExit('PolyForge requires Python 3.11+ (standard-library tomllib).')


class ConfigError(Exception):
    """A configuration or path-containment failure."""


ROUTE_KEYS = ('scout_agent', 'architect_agent', 'default_worker',
              'complex_worker', 'followup_architect_agent', 'major_complex_worker',
              'rescue_worker', 'reviewer_agent')
PACKAGE_DIRS = ('agents', 'codex-agents', 'config', 'references', 'scripts', 'templates')
NAME = re.compile(r'polyforge-[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def contained(root: Path, path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ConfigError(f'Path escapes intended directory: {path}')
    return resolved


def destination(root: Path, path: Path) -> Path:
    # Never redirect managed writes through existing symlinks or junctions.
    # The caller's explicitly chosen root has already been resolved.
    candidate = root
    for part in path.relative_to(root).parts:
        candidate = candidate / part
        if candidate.is_symlink() or getattr(candidate, 'is_junction', lambda: False)():
            raise ConfigError(f'Redirected destination is not allowed: {candidate}')
    return contained(root, path)


def read_toml(path: Path) -> tuple[str, dict]:
    try:
        raw = path.read_text(encoding='utf-8')
        return raw, tomllib.loads(raw)
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f'Cannot parse {path}: {exc}') from exc


def settings(cfg: dict, section: str, name: str | None = None) -> dict:
    entry = cfg.get(section)
    if not isinstance(entry, dict):
        raise ConfigError(f'Missing role section [{section}]')
    model, effort = entry.get('model'), entry.get('reasoning_effort')
    if not isinstance(model, str) or not isinstance(effort, str):
        raise ConfigError(f'Model and effort must be strings in [{section}]')
    supported = cfg.get('model_support', {}).get(model, [])
    if not supported or effort not in supported:
        raise ConfigError(f'Unsupported offline model/effort: [{section}] {model}/{effort}')
    expected = {'model': model, 'model_reasoning_effort': effort}
    if name is not None:
        sandbox = entry.get('sandbox_mode')
        if sandbox not in {'read-only', 'workspace-write'}:
            raise ConfigError(f'Invalid sandbox for [{section}]: {sandbox}')
        expected.update(name=name, sandbox_mode=sandbox)
    return expected


def load_config(root: Path) -> dict:
    _, cfg = read_toml(contained(root, root / 'config/model-router.toml'))
    for table in ('roles', 'router', 'model_support', 'release'):
        if not isinstance(cfg.get(table), dict):
            raise ConfigError(f'Missing or invalid [{table}] table')
    for model, efforts in cfg['model_support'].items():
        if not isinstance(efforts, list) or not efforts or not all(isinstance(e, str) for e in efforts):
            raise ConfigError(f'Invalid effort allowlist for {model}')
    roles, router = cfg.get('roles'), cfg.get('router', {})
    if not isinstance(roles, dict) or not roles:
        raise ConfigError('Missing [roles] bindings')
    for name, section in roles.items():
        if not NAME.fullmatch(name) or not isinstance(section, str):
            raise ConfigError(f'Invalid role binding: {name}')
        settings(cfg, section, name)
    settings(cfg, 'orchestrator')
    known = {name + '.toml' for name in roles}
    retirement = cfg.get('retired', {})
    if not isinstance(retirement, dict):
        raise ConfigError('Invalid [retired] table')
    retired = retirement.get('role_files', [])
    if not isinstance(retired, list):
        raise ConfigError('retired.role_files must be a list')
    if any(not isinstance(name, str) or not name.endswith('.toml') or not NAME.fullmatch(name[:-5]) for name in retired):
        raise ConfigError('Retired role names must be safe PolyForge TOML filenames')
    if len(set(retired)) != len(retired) or set(retired) & known:
        raise ConfigError('Retired roles must be distinct and cannot be active roles')
    unbound = {p.name for p in (root / 'codex-agents').glob('*.toml')} - known
    if unbound:
        raise ConfigError('Unbound repository roles: ' + ', '.join(sorted(unbound)))
    for key in ROUTE_KEYS:
        if not isinstance(router.get(key), str) or router[key] not in roles:
            raise ConfigError(f'Unknown route binding: router.{key}={router.get(key)}')
    for key in ('escalation_chain', 'major_escalation_chain'):
        chain = router.get(key)
        middle = router['complex_worker' if key == 'escalation_chain' else 'major_complex_worker']
        expected = [router['default_worker'], middle, router['rescue_worker']]
        if chain != expected or len(set(chain)) != len(chain):
            raise ConfigError(f'{key} must be direct default-worker -> Sol -> rescue')
    for key in ('major_initial_design_requires_astra', 'major_followup_requires_astra_baseline',
                'major_fundamental_redesign_requires_astra'):
        if router.get(key) is not True:
            raise ConfigError(f'Required major boundary disabled: {key}')
    for key in ('architect_agent', 'rescue_worker'):
        if cfg[roles[router[key]]]['model'] != 'gpt-6-astra':
            raise ConfigError(f'{key} must use Astra')
    for key, effort in (('followup_architect_agent', 'high'), ('major_complex_worker', 'max')):
        role = cfg[roles[router[key]]]
        if (role['model'], role['reasoning_effort']) != ('gpt-6.1-sol', effort):
            raise ConfigError(f'{key} must use GPT-6.1 Sol {effort}')
    for key in ('scout_agent', 'architect_agent', 'followup_architect_agent', 'reviewer_agent'):
        if cfg[roles[router[key]]]['sandbox_mode'] != 'read-only':
            raise ConfigError(f'{key} must remain read-only')
    for key in ('default_worker', 'complex_worker', 'major_complex_worker', 'rescue_worker'):
        if cfg[roles[router[key]]]['sandbox_mode'] != 'workspace-write':
            raise ConfigError(f'{key} requires workspace-write')
    version = cfg.get('release', {}).get('version')
    if not isinstance(version, str) or not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ConfigError('Invalid release version')
    skill = contained(root, root / 'SKILL.md').read_text(encoding='utf-8')
    readme = contained(root, root / 'README.md').read_text(encoding='utf-8')
    if not re.search(r'^  version:\s*"' + re.escape(version) + r'"\s*$', skill, re.M):
        raise ConfigError('SKILL release version disagrees with router')
    if f'PolyForge v{version} ' not in readme:
        raise ConfigError('README release version disagrees with router')
    return cfg


def role_paths(root: Path, cfg: dict):
    role_root = contained(root, root / 'codex-agents')
    for name, section in cfg['roles'].items():
        yield name, contained(role_root, role_root / f'{name}.toml'), settings(cfg, section, name)


def render_role(raw: str, expected: dict) -> str:
    marker = re.search(r'^developer_instructions\s*=', raw, re.M)
    if marker is None:
        raise ConfigError('Role must contain developer_instructions')
    header, body = raw[:marker.start()], raw[marker.start():]
    for key, value in expected.items():
        pattern = re.compile(r'^' + re.escape(key) + r'\s*=.*$', re.M)
        if len(pattern.findall(header)) != 1:
            raise ConfigError(f'Role header must define {key} exactly once')
        header = pattern.sub(lambda _: f'{key} = {json.dumps(value, ensure_ascii=False)}', header)
    rendered = header + body
    parsed = tomllib.loads(rendered)
    if any(parsed.get(key) != value for key, value in expected.items()):
        raise ConfigError('Rendered role settings disagree with router')
    return rendered


def check_repo(root: Path, cfg: dict) -> None:
    errors = []
    for name, path, expected in role_paths(root, cfg):
        raw, actual = read_toml(path)
        if not isinstance(actual.get('developer_instructions'), str) or not actual['developer_instructions'].strip():
            errors.append(f'{name}: missing developer instructions')
        render_role(raw, expected)
        for key, value in expected.items():
            if actual.get(key) != value:
                errors.append(f'{name}: {key}={actual.get(key)!r}, expected {value!r}')
    if errors:
        raise ConfigError('\n'.join(errors) + '\nRun --sync-repo after reviewing configuration.')


def sync_repo(root: Path, cfg: dict) -> int:
    planned = []
    for _, path, expected in role_paths(root, cfg):
        raw, actual = read_toml(path)
        if not isinstance(actual.get('developer_instructions'), str) or not actual['developer_instructions'].strip():
            raise ConfigError(f'Missing developer instructions: {path}')
        rendered = render_role(raw, expected)
        if raw != rendered:
            planned.append((path, rendered))
    # Validate all templates and destinations before writing any file.
    for path, rendered in planned:
        path.write_text(rendered, encoding='utf-8', newline='\n')
    check_repo(root, cfg)
    return len(planned)


def payload(root: Path, cfg: dict) -> dict[Path, bytes]:
    files = [root / 'SKILL.md', root / 'README.md']
    for directory in PACKAGE_DIRS:
        base = contained(root, root / directory)
        for path in sorted(base.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                contained(base, path)
                files.append(path)
    result = {Path('skills/polyforge') / path.relative_to(root): path.read_bytes() for path in files}
    for name, path, _ in role_paths(root, cfg):
        result[Path('agents') / f'{name}.toml'] = path.read_bytes()
    return result


def target(home: Path, relative: Path) -> Path:
    intended = home / ('agents' if relative.parts[0] == 'agents' else 'skills/polyforge')
    destination(home, intended)
    destination(home, home / relative)
    return contained(intended, home / relative)


def retired_paths(cfg: dict):
    for filename in cfg.get('retired', {}).get('role_files', []):
        yield Path('agents') / filename
        yield Path('skills/polyforge/codex-agents') / filename


def check_installed(root: Path, cfg: dict, home: Path) -> None:
    errors = []
    for relative, data in payload(root, cfg).items():
        path = target(home, relative)
        if not path.is_file():
            errors.append(f'Missing installed file: {relative}')
        elif path.read_bytes() != data:
            errors.append(f'Installed drift: {relative}')
    for relative in retired_paths(cfg):
        if target(home, relative).exists():
            errors.append(f'Retired installed role remains: {relative}')
    if errors:
        raise ConfigError('\n'.join(errors))


def install(root: Path, cfg: dict, home: Path, dry_run: bool) -> tuple[int, Path | None]:
    planned = []
    for relative, data in payload(root, cfg).items():
        path = target(home, relative)
        if path.exists() and not path.is_file():
            raise ConfigError(f'Installation target is not a file: {path}')
        old = path.read_bytes() if path.is_file() else None
        if old != data:
            planned.append((relative, path, data, old))
    for relative in retired_paths(cfg):
        path = target(home, relative)
        if path.exists():
            if not path.is_file():
                raise ConfigError(f'Retired role target is not a file: {path}')
            planned.append((relative, path, None, path.read_bytes()))
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    backup_root = home / 'polyforge-backups'
    destination(home, backup_root)
    backup = contained(backup_root, backup_root / stamp)
    backup_files = [(contained(backup, backup / relative), old)
                    for relative, _, _, old in planned if old is not None]
    if dry_run:
        for relative, _, data, old in planned:
            action = 'DELETE (after backup)' if data is None else ('UPDATE' if old is not None else 'CREATE')
            print(f'{action} {relative}')
        print(f'Dry run: {len(planned)} file(s), {len(backup_files)} backup(s); no writes.')
        return len(planned), None
    # Back up all replaced files before replacing any target.
    for path, old in backup_files:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(old)
    for _, path, data, _ in planned:
        if data is None:
            path.unlink()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    check_installed(root, cfg, home)
    return len(planned), backup if backup_files else None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('--check', action='store_true', help='Read-only repository check (default)')
    actions.add_argument('--sync-repo', action='store_true', help='Sync managed headers from router')
    actions.add_argument('--install', action='store_true', help='Explicitly install skill and roles')
    actions.add_argument('--check-installed', action='store_true', help='Read-only installed check')
    parser.add_argument('--codex-home', type=Path, help='Override CODEX_HOME or ~/.codex')
    parser.add_argument('--dry-run', action='store_true', help='Preview --install without writing')
    args = parser.parse_args(argv)
    if args.dry_run and not args.install:
        parser.error('--dry-run requires --install')
    root = args.root.expanduser().resolve()
    home = (args.codex_home or Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex')).expanduser().resolve()
    try:
        cfg = load_config(root)
        if args.sync_repo:
            print(f'Synchronized {sync_repo(root, cfg)} role file(s).')
        else:
            check_repo(root, cfg)
            if args.install:
                count, backup = install(root, cfg, home, args.dry_run)
                if not args.dry_run:
                    print(f'Installed/updated/retired {count} file(s). Backup: {backup or "not needed"}')
                    print('Start a new/reloaded session; select GPT-6.1 Sol high for the main task separately.')
            elif args.check_installed:
                check_installed(root, cfg, home)
                print('Installed package and roles match this release.')
            else:
                print(f'PolyForge {cfg["release"]["version"]}: repository check passed ({len(cfg["roles"])} roles).')
        return 0
    except (ConfigError, OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

