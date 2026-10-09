"""Deterministic checker regressions; no Codex, network, or business I/O."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

from check_structure import audit_package, validate_model_options


MODELS = ("gpt-6-astra", "gpt-6.1-sol", "gpt-6-luna")
EFFORTS = ("low", "medium", "high", "xhigh", "max")
MODEL_TABLE = "\n".join([
    "| 模型 ID | 推理等级 | 任务 | 调整 |",
    "| --- | --- | --- | --- |",
    *(f"| `{m}` | `{e}` | synthetic | check |" for m in MODELS for e in EFFORTS),
    "\n| 模型 ID | 模式 | 限制 |",
    "| --- | --- | --- |",
    "| `gpt-6-astra` | `ultra` | host-dependent |",
    "| `gpt-6.1-sol` | `ultra` | host-dependent |",
]) + "\n"
METADATA = {
    "status": "test", "owner": "synthetic", "last_verified": "2026-10-09",
    "verified_commit": "fixture", "applies_to": ["adaptive-task-router"],
}


def governed(body: str, name: str | None = None) -> str:
    header = METADATA if name is None else {
        "name": name, "description": "Synthetic test skill", "metadata": METADATA,
    }
    return "---\n" + yaml.safe_dump(header, sort_keys=False) + "---\n\n" + body


class ModelTableTests(unittest.TestCase):
    def test_valid_seventeen(self):
        self.assertEqual(validate_model_options(MODEL_TABLE), (17, []))

    def test_appended_invalid_options(self):
        # Unlike the old filter, unknown names remain visible to validation.
        for model, effort in (
            ("gpt-6-sol", "high"), ("gpt-6.1-so1", "high"),
            ("other-model", "high"), ("gpt-6.1-sol", "hgh"),
            ("gpt-6-luna", "ultra"),
        ):
            with self.subTest(model=model, effort=effort):
                count, errors = validate_model_options(
                    MODEL_TABLE + f"| `{model}` | `{effort}` | extra |\n")
                self.assertEqual(count, 18)
                self.assertTrue(any("unknown model option" in error for error in errors))

    def test_replaced_old_model(self):
        _, errors = validate_model_options(MODEL_TABLE.replace("gpt-6.1-sol", "gpt-6-sol", 1))
        self.assertTrue(any("unknown" in error for error in errors))
        self.assertTrue(any("missing" in error for error in errors))

    def test_duplicate(self):
        _, errors = validate_model_options(MODEL_TABLE + "| `gpt-6-astra` | `low` | extra |\n")
        self.assertTrue(any("duplicate" in error for error in errors))

    def test_missing(self):
        text = "\n".join(line for line in MODEL_TABLE.splitlines()
                         if not line.startswith("| `gpt-6-astra` | `low`"))
        self.assertTrue(any("missing" in error for error in validate_model_options(text)[1]))

    def test_unquoted_unknown(self):
        self.assertTrue(validate_model_options(MODEL_TABLE + "| misspelled | high | extra |\n")[1])

    def test_plain_valid_cells(self):
        self.assertEqual(validate_model_options(MODEL_TABLE.replace("`", "")), (17, []))

    def test_bad_row_shapes(self):
        for extra in ("| `bad` | `high` |", "| `bad` | `high` | x", "| `` | `high` | x |"):
            with self.subTest(extra=extra):
                self.assertTrue(validate_model_options(MODEL_TABLE + extra + "\n")[1])

    def test_fenced_example_not_an_option(self):
        for fence in ("```", "~~~~"):
            text = MODEL_TABLE + f"\n{fence}text\n| `example` | `high` | x |\n{fence}\n"
            self.assertEqual(validate_model_options(text), (17, []))

    def test_unclosed_fence(self):
        self.assertTrue(validate_model_options(MODEL_TABLE + "```text\nexample\n")[1])

    def test_headers_do_not_hide_unknown_row(self):
        self.assertTrue(validate_model_options(MODEL_TABLE + "| 模型 ID | `hgh` | extra |\n")[1])


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="router-checker-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.put_json(".codex-plugin/plugin.json", {
            "name": "adaptive-task-router", "version": "0.2.1+test", "skills": "./skills/",
        })
        self.put_json(".agents/plugins/marketplace.json", {
            "name": "afd2-sol61", "plugins": [{
                "name": "adaptive-task-router", "source": {"source": "local", "path": "."},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Productivity",
            }],
        })
        self.put("LICENSE", "MIT License\nSynthetic test specimen, not a distributed license.\n")
        for name, implicit in (("route-task", False), ("suggest-task-routing", True)):
            self.put(f"skills/{name}/SKILL.md", governed("# Synthetic skill\n", name))
            self.put(f"skills/{name}/agents/openai.yaml", yaml.safe_dump({
                "policy": {"allow_implicit_invocation": implicit},
                "interface": {"default_prompt": f"Use ${name}",
                              "short_description": "Synthetic interface for deterministic tests"},
            }))
        self.put("skills/route-task/references/model-routing.md", governed(MODEL_TABLE))

    def put(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def put_json(self, relative, value):
        self.put(relative, json.dumps(value))

    def result(self):
        return audit_package(self.root)

    def assert_failure(self, fragment):
        result = self.result()
        self.assertFalse(result["passed"])
        self.assertTrue(any(fragment in error for error in result["failures"]), result)

    def test_valid_package(self):
        self.assertTrue(self.result()["passed"], self.result())
        self.assertEqual(self.result()["model_options"], 17)

    def test_missing_manifest(self):
        (self.root / ".codex-plugin/plugin.json").unlink()
        self.assert_failure("FileNotFoundError")

    def test_malformed_json(self):
        self.put(".codex-plugin/plugin.json", "{")
        self.assert_failure("invalid data")

    def test_nonmapping_json(self):
        self.put_json(".codex-plugin/plugin.json", [])
        self.assert_failure("expected mapping")

    def test_bad_manifest_fields(self):
        for field, value, error in (
            ("name", "other", "plugin identity"), ("version", None, "release version"),
            ("skills", "other", "discovery path"), ("mcpServers", {}, "runtime dependency"),
        ):
            with self.subTest(field=field):
                self.put_json(".codex-plugin/plugin.json", {
                    "name": "adaptive-task-router", "version": "0.2.1", "skills": "./skills/", field: value,
                })
                self.assert_failure(error)

    def test_invalid_marketplace(self):
        for entries in (None, [], [{}], ["bad"], [{}, {}]):
            with self.subTest(entries=entries):
                self.put_json(".agents/plugins/marketplace.json", {"name": "afd2-sol61", "plugins": entries})
                self.assertFalse(self.result()["passed"])

    def test_other_source(self):
        path = self.root / ".agents/plugins/marketplace.json"
        value = json.loads(path.read_text())
        value["plugins"][0]["source"] = {"source": "github", "repo": "other/source"}
        self.put_json(".agents/plugins/marketplace.json", value)
        self.assert_failure("local source")

    def test_missing_skill(self):
        (self.root / "skills/route-task/SKILL.md").unlink()
        self.assert_failure("missing SKILL.md")

    def test_bad_yaml_and_shape(self):
        for text in ("key: [", "[]\n", "interface: []\npolicy: []\n"):
            with self.subTest(text=text):
                self.put("skills/route-task/agents/openai.yaml", text)
                self.assertFalse(self.result()["passed"])

    def test_changed_invocation_policy(self):
        path = self.root / "skills/route-task/agents/openai.yaml"
        value = yaml.safe_load(path.read_text())
        value["policy"]["allow_implicit_invocation"] = True
        self.put(path.relative_to(self.root), yaml.safe_dump(value))
        self.assert_failure("invocation policy")

    def test_bad_metadata(self):
        for text in ("no header\n", "---\nmetadata: []\n---\n", "---\nowner: [\n---\n"):
            with self.subTest(text=text):
                self.put("README.md", text)
                self.assertFalse(self.result()["passed"])

    def test_missing_and_escaping_links(self):
        for target in ("missing.md", "../outside.md"):
            with self.subTest(target=target):
                self.put("README.md", governed(f"[link]({target})\n"))
                self.assertFalse(self.result()["passed"])

    def test_cross_skill_links_allowed_in_complete_package(self):
        self.put("skills/route-task/SKILL.md", governed(
            "[suggest](../suggest-task-routing/SKILL.md)\n", "route-task"))
        self.assertTrue(self.result()["passed"], self.result())

    def test_external_links_not_fetched(self):
        self.put("README.md", governed("[official](https://example.invalid/no-network)\n"))
        self.assertTrue(self.result()["passed"])

    def test_extra_bad_option_rejected_at_package_level(self):
        self.put("skills/route-task/references/model-routing.md", governed(
            MODEL_TABLE + "| `gpt-6-sol` | `high` | extra |\n"))
        self.assert_failure("unknown model option")

    def test_cli_json_and_exit_codes(self):
        # Run the real main() against this specimen, without modifying the repository.
        tests_dir = str(Path(__file__).resolve().parent)
        code = ("import sys; from pathlib import Path; "
                "sys.path.insert(0, sys.argv[1]); import check_structure as c; "
                "c.ROOT=Path(sys.argv[2]); raise SystemExit(c.main())")
        for invalid in (False, True):
            if invalid:
                self.put(".codex-plugin/plugin.json", "{")
            run = subprocess.run([sys.executable, "-B", "-c", code, tests_dir, str(self.root)],
                                 capture_output=True, text=True, timeout=10, check=False)
            self.assertEqual(run.returncode, 1 if invalid else 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)["passed"], not invalid)


if __name__ == "__main__":
    unittest.main()
