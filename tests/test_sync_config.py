"""Observable synchronization and installation regression checks."""
import contextlib
import importlib.util
import io
from pathlib import Path
import shutil
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sync_config', SOURCE / 'scripts/sync-config.py')
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class SyncConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='polyforge-test-', dir=SOURCE.parent)
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / 'polyforge'
        shutil.copytree(SOURCE, self.root, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        self.home = self.base / 'codex'

    def change_router(self, old, new):
        path = self.root / 'config/model-router.toml'
        raw = path.read_text(encoding='utf-8')
        self.assertIn(old, raw)
        path.write_text(raw.replace(old, new, 1), encoding='utf-8')

    def cfg(self):
        return sync.load_config(self.root)

    def snapshot(self, path):
        return {p.relative_to(path): p.read_bytes() for p in path.rglob('*') if p.is_file()}

    def test_release_and_role_configuration_pass(self):
        cfg = self.cfg()
        sync.check_repo(self.root, cfg)
        self.assertEqual(cfg['architect']['model'], 'gpt-6-astra')
        self.assertEqual(cfg['architect']['reasoning_effort'], 'high')
        self.assertEqual(cfg['astra']['reasoning_effort'], 'high')
        for role in ('major_worker',):
            self.assertEqual((cfg[role]['model'], cfg[role]['reasoning_effort']), ('gpt-6.1-sol', 'max'))
        for role in ('orchestrator', 'refiner', 'complex', 'reviewer'):
            self.assertEqual((cfg[role]['model'], cfg[role]['reasoning_effort']), ('gpt-6.1-sol', 'high'))
        self.assertEqual(cfg['luna']['reasoning_effort'], 'max')
        self.assertEqual(cfg['scout']['reasoning_effort'], 'medium')
        self.assertEqual(len(cfg['roles']), 8)
        self.assertNotIn('luna56', cfg)
        self.assertNotIn('gpt-5.6-luna', cfg['model_support'])
        self.assertFalse((self.root / 'codex-agents/polyforge-luna56.toml').exists())

    def test_default_check_creates_no_destination(self):
        before = self.snapshot(self.root)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.main(['--root', str(self.root), '--codex-home', str(self.home)]), 0)
        self.assertFalse(self.home.exists())
        self.assertEqual(before, self.snapshot(self.root))

    def test_unknown_model_fails_without_writes(self):
        self.change_router('model = "gpt-6.1-sol"', 'model = "unknown-model"')
        before = self.snapshot(self.root)
        with self.assertRaisesRegex(sync.ConfigError, 'Unsupported offline'):
            self.cfg()
        self.assertEqual(before, self.snapshot(self.root))

    def test_sol_none_is_rejected(self):
        self.change_router('[orchestrator]\nmodel = "gpt-6.1-sol"\nreasoning_effort = "high"',
                           '[orchestrator]\nmodel = "gpt-6.1-sol"\nreasoning_effort = "none"')
        with self.assertRaisesRegex(sync.ConfigError, 'Unsupported offline'):
            self.cfg()

    def test_non_string_model_fails_clearly(self):
        self.change_router('model = "gpt-6.1-sol"', 'model = []')
        with self.assertRaisesRegex(sync.ConfigError, 'must be strings'):
            self.cfg()

    def test_unknown_route_rejected(self):
        self.change_router('default_worker = "polyforge-luna"', 'default_worker = "polyforge-missing"')
        with self.assertRaisesRegex(sync.ConfigError, 'Unknown route binding'):
            self.cfg()

    def test_drift_detected_and_sync_preserves_instructions_and_custom_field(self):
        path = self.root / 'codex-agents/polyforge-complex.toml'
        original = sync.read_toml(path)[1]
        raw = path.read_text(encoding='utf-8').replace('model = "gpt-6.1-sol"', 'model = "gpt-6-sol"')
        raw = 'custom_note = "preserve me"\n' + raw
        path.write_text(raw, encoding='utf-8')
        cfg = self.cfg()
        with self.assertRaisesRegex(sync.ConfigError, 'polyforge-complex: model'):
            sync.check_repo(self.root, cfg)
        self.assertEqual(sync.sync_repo(self.root, cfg), 1)
        actual = sync.read_toml(path)[1]
        self.assertEqual(actual['developer_instructions'], original['developer_instructions'])
        self.assertEqual(actual['description'], original['description'])
        self.assertEqual(actual['custom_note'], 'preserve me')
        self.assertEqual(actual['model'], 'gpt-6.1-sol')
        self.assertEqual(sync.sync_repo(self.root, cfg), 0)

    def test_sync_validates_all_templates_before_writing(self):
        first = self.root / 'codex-agents/polyforge-scout.toml'
        first.write_text(first.read_text(encoding='utf-8').replace('"medium"', '"high"', 1), encoding='utf-8')
        last = self.root / 'codex-agents/polyforge-astra.toml'
        last.write_text(last.read_text(encoding='utf-8').replace('developer_instructions', 'wrong_instructions'), encoding='utf-8')
        before = self.snapshot(self.root)
        with self.assertRaises(sync.ConfigError):
            sync.sync_repo(self.root, self.cfg())
        self.assertEqual(before, self.snapshot(self.root))

    def test_intermediate_luna_tier_rejected(self):
        self.change_router('escalation_chain = ["polyforge-luna", "polyforge-complex", "polyforge-astra"]',
                           'escalation_chain = ["polyforge-luna", "polyforge-luna56", "polyforge-complex", "polyforge-astra"]')
        with self.assertRaisesRegex(sync.ConfigError, 'must be direct'):
            self.cfg()

    def test_first_major_design_cannot_switch_to_sol(self):
        self.change_router('[architect]\nmodel = "gpt-6-astra"', '[architect]\nmodel = "gpt-6.1-sol"')
        with self.assertRaisesRegex(sync.ConfigError, 'architect_agent must use Astra'):
            self.cfg()

    def test_major_followup_efforts_cannot_silently_change(self):
        for section, expected, wrong in (('refiner', 'high', 'max'), ('major_worker', 'max', 'high')):
            with self.subTest(section=section):
                old = f'[{section}]\nmodel = "gpt-6.1-sol"\nreasoning_effort = "{expected}"'
                new = f'[{section}]\nmodel = "gpt-6.1-sol"\nreasoning_effort = "{wrong}"'
                self.change_router(old, new)
                with self.assertRaisesRegex(sync.ConfigError, f'must use GPT-6.1 Sol {expected}'):
                    self.cfg()
                self.change_router(new, old)

    def test_micro_edit_safety_gate_required(self):
        self.change_router('micro_edits_require_low_risk = true', 'micro_edits_require_low_risk = false')
        with self.assertRaisesRegex(sync.ConfigError, 'Micro-edit safety gate'):
            self.cfg()

    def test_invalid_toml_rejected(self):
        path = self.root / 'config/model-router.toml'
        path.write_text(path.read_text(encoding='utf-8') + '\nbroken = [', encoding='utf-8')
        with self.assertRaisesRegex(sync.ConfigError, 'Cannot parse'):
            self.cfg()

    def test_conflicting_micro_edit_policy_rejected(self):
        self.change_router('orchestrator_production_edits_integration_only = false',
                           'orchestrator_production_edits_integration_only = true')
        with self.assertRaisesRegex(sync.ConfigError, 'conflicts with integration-only'):
            self.cfg()

    def test_install_backs_up_old_roles_and_preserves_user_config(self):
        (self.home / 'agents').mkdir(parents=True)
        user_config = b'[agents]\nmax_threads = 4\n'
        (self.home / 'config.toml').write_bytes(user_config)
        unrelated = b'custom-role-content\n'
        (self.home / 'agents/my-custom-role.toml').write_bytes(unrelated)
        (self.home / 'agents/polyforge-terra.toml').write_bytes(unrelated)
        old = b'model = "old-model"\n'
        (self.home / 'agents/polyforge-reviewer.toml').write_bytes(old)
        count, backup = sync.install(self.root, self.cfg(), self.home, False)
        self.assertGreater(count, 9)
        self.assertEqual((backup / 'agents/polyforge-reviewer.toml').read_bytes(), old)
        self.assertEqual((self.home / 'config.toml').read_bytes(), user_config)
        for name in ('my-custom-role.toml', 'polyforge-terra.toml'):
            self.assertEqual((self.home / 'agents' / name).read_bytes(), unrelated)
        sync.check_installed(self.root, self.cfg(), self.home)
        self.assertFalse((self.home / 'skills/polyforge/tests').exists())

    def test_install_is_idempotent(self):
        cfg = self.cfg()
        sync.install(self.root, cfg, self.home, False)
        before = self.snapshot(self.home)
        mtimes = {p: p.stat().st_mtime_ns for p in self.home.rglob('*') if p.is_file()}
        self.assertEqual(sync.install(self.root, cfg, self.home, False), (0, None))
        self.assertEqual(before, self.snapshot(self.home))
        self.assertEqual(mtimes, {p: p.stat().st_mtime_ns for p in self.home.rglob('*') if p.is_file()})

    def test_dry_run_does_not_create_or_overwrite_files(self):
        cfg = self.cfg()
        with contextlib.redirect_stdout(io.StringIO()):
            sync.install(self.root, cfg, self.home, True)
        self.assertFalse(self.home.exists())
        (self.home / 'agents').mkdir(parents=True)
        (self.home / 'agents/polyforge-luna.toml').write_bytes(b'old\n')
        before = self.snapshot(self.home)
        with contextlib.redirect_stdout(io.StringIO()):
            sync.install(self.root, cfg, self.home, True)
        self.assertEqual(before, self.snapshot(self.home))
        self.assertFalse((self.home / 'polyforge-backups').exists())

    def test_installed_drift_check_is_read_only(self):
        cfg = self.cfg()
        sync.install(self.root, cfg, self.home, False)
        path = self.home / 'agents/polyforge-reviewer.toml'
        path.write_bytes(b'locally-edited\n')
        before = self.snapshot(self.home)
        with self.assertRaisesRegex(sync.ConfigError, 'Installed drift'):
            sync.check_installed(self.root, cfg, self.home)
        self.assertEqual(before, self.snapshot(self.home))

    def test_path_traversal_rejected(self):
        with self.assertRaisesRegex(sync.ConfigError, 'escapes intended'):
            sync.contained(self.home, self.home / '../outside.txt')

    def test_role_name_path_traversal_rejected(self):
        self.change_router('polyforge-scout = "scout"', '"../outside" = "scout"')
        with self.assertRaisesRegex(sync.ConfigError, 'Invalid role binding'):
            self.cfg()

    def test_redirected_install_rejected_before_any_writes(self):
        self.home.mkdir()
        outside = self.base / 'outside'
        outside.mkdir()
        try:
            (self.home / 'agents').symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f'Symlink creation unavailable: {exc}')
        with self.assertRaisesRegex(sync.ConfigError, 'Redirected destination'):
            sync.install(self.root, self.cfg(), self.home, False)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((self.home / 'skills').exists())

    def test_retired_roles_are_backed_up_and_removed_on_upgrade(self):
        cfg = self.cfg()
        old = b'old-compatibility-role\n'
        paths = list(sync.retired_paths(cfg))
        for relative in paths:
            path = self.home / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(old)
        _, backup = sync.install(self.root, cfg, self.home, False)
        for relative in paths:
            self.assertFalse((self.home / relative).exists())
            self.assertEqual((backup / relative).read_bytes(), old)
        sync.check_installed(self.root, cfg, self.home)
        self.assertEqual(sync.install(self.root, cfg, self.home, False), (0, None))

    def test_retired_dry_run_and_check_do_not_delete(self):
        cfg = self.cfg()
        sync.install(self.root, cfg, self.home, False)
        path = self.home / 'agents/polyforge-luna56.toml'
        path.write_bytes(b'old\n')
        before = self.snapshot(self.home)
        with self.assertRaisesRegex(sync.ConfigError, 'Retired installed role remains'):
            sync.check_installed(self.root, cfg, self.home)
        with contextlib.redirect_stdout(io.StringIO()) as output:
            sync.install(self.root, cfg, self.home, True)
        self.assertIn('DELETE (after backup)', output.getvalue())
        self.assertEqual(before, self.snapshot(self.home))

    def test_retirement_path_traversal_rejected(self):
        self.change_router('role_files = ["polyforge-luna56.toml"]', 'role_files = ["../outside.toml"]')
        with self.assertRaisesRegex(sync.ConfigError, 'safe PolyForge TOML'):
            self.cfg()

    def test_active_role_cannot_be_retired(self):
        self.change_router('role_files = ["polyforge-luna56.toml"]', 'role_files = ["polyforge-scout.toml"]')
        with self.assertRaisesRegex(sync.ConfigError, 'cannot be active'):
            self.cfg()


if __name__ == '__main__':
    unittest.main()
