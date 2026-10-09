"""Audit package structure and references; this does not test model behavior."""

from pathlib import Path
import json
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
failures = []
link_count = 0
document_count = 0


def require(condition, message):
    if not condition:
        failures.append(message)


manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
require(manifest["name"] == "adaptive-task-router", "plugin identity differs")
require(manifest["version"].split("+")[0] == "0.2.0", "unexpected release version")
require(manifest.get("skills") == "./skills/", "skills discovery path differs")
require(not any(k in manifest for k in ("apps", "mcpServers")), "unexpected runtime dependency")

marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
require(marketplace.get("name") == "afd2-sol61", "local marketplace identity differs")
entries = marketplace.get("plugins", [])
require(len(entries) == 1, "local marketplace must expose exactly this plugin")
if len(entries) == 1:
    entry = entries[0]
    require(entry.get("name") == manifest["name"], "marketplace/plugin identity differs")
    require(entry.get("source") == {
        "source": "local", "path": "."
    }, "local source must resolve to this complete package")
    require(entry.get("policy") == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "unexpected installation policy")
    require(entry.get("category") == "Productivity", "unexpected marketplace category")
require((ROOT / "LICENSE").read_text(encoding="utf-8").startswith("MIT License"), "missing MIT license")

for name, implicit in (("route-task", False), ("suggest-task-routing", True)):
    folder = ROOT / "skills" / name
    ui = yaml.safe_load((folder / "agents/openai.yaml").read_text(encoding="utf-8"))
    require(ui["policy"]["allow_implicit_invocation"] is implicit, f"{name}: invocation policy")
    require(f"${name}" in ui["interface"]["default_prompt"], f"{name}: default prompt invocation")
    require(25 <= len(ui["interface"]["short_description"]) <= 64, f"{name}: UI description length")

for path in sorted(ROOT.rglob("*.md")):
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT).as_posix()
    # Synthetic task inputs intentionally are not governed plugin instructions.
    if not rel.startswith("tests/fixtures/"):
        require(text.startswith("---\n"), f"{rel}: missing metadata")
        if text.startswith("---\n"):
            header = yaml.safe_load(text.split("---", 2)[1])
            governed = header.get("metadata", header)
            for key in ("status", "owner", "last_verified", "verified_commit", "applies_to"):
                require(key in governed, f"{rel}: missing {key}")
            if path.name == "SKILL.md":
                require(header.get("name") == path.parent.name, f"{rel}: skill identity")
                require(bool(header.get("description")), f"{rel}: missing description")
            document_count += 1
    require("[TODO:" not in text and "[INSERT" not in text, f"{rel}: unfinished scaffold")
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
        target = target.split("#", 1)[0].strip("<>")
        if not target or re.match(r"[a-zA-Z][\w+.-]*:", target):
            continue
        resolved = (path.parent / target).resolve()
        require(resolved.is_relative_to(ROOT), f"{rel}: reference escapes package: {target}")
        require(resolved.exists(), f"{rel}: missing reference: {target}")
        link_count += 1

reference = (ROOT / "skills/route-task/references/model-routing.md").read_text(encoding="utf-8")
combinations = re.findall(r"\| `(gpt-(?:6-(?:astra|luna)|6\.1-sol))` \| `(\w+)` \|", reference)
expected = {(model, effort) for model in ("gpt-6-astra", "gpt-6.1-sol", "gpt-6-luna")
            for effort in ("low", "medium", "high", "xhigh", "max")}
expected |= {("gpt-6-astra", "ultra"), ("gpt-6.1-sol", "ultra")}
require(len(combinations) == 17 and set(combinations) == expected, "17-option coverage differs")

print(json.dumps({"passed": not failures, "documents": document_count,
                  "local_links": link_count, "model_options": len(combinations),
                  "failures": failures}, ensure_ascii=False, indent=2))
sys.exit(1 if failures else 0)
