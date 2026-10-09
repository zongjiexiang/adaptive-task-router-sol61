"""Check the complete plugin package; static checks do not prove agent behavior."""

from collections import Counter
import json
from pathlib import Path
import re
import sys
import tomllib

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PARSERS = {".json": json.loads, ".yaml": yaml.safe_load,
                  ".yml": yaml.safe_load, ".toml": tomllib.loads}
UNSUPPORTED_CONFIG_SUFFIXES = {".json5", ".jsonc", ".ini", ".cfg", ".conf"}
EXPECTED_OPTIONS = {
    (model, effort)
    for model in ("gpt-6-astra", "gpt-6.1-sol", "gpt-6-luna")
    for effort in ("low", "medium", "high", "xhigh", "max")
} | {("gpt-6-astra", "ultra"), ("gpt-6.1-sol", "ultra")}


def validate_model_options(text: str) -> tuple[int, list[str]]:
    """Read ALL table data rows, before checking the supported policy options.

    This file contains only model tables. New table formats must be introduced
    deliberately rather than silently filtering out unknown model names.
    Border pipes are optional. Any pipe-containing line outside a fence is
    checked, so unsupported row syntax cannot silently hide model options.
    Fenced examples are not Markdown tables and do not contribute options.
    """
    options: list[tuple[str, str]] = []
    failures: list[str] = []
    fence: tuple[str, int] | None = None
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        marker = re.match(r"^(`{3,}|~{3,})(.*)$", line)
        if marker:
            token, suffix = marker.groups()
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1] and not suffix.strip():
                fence = None
            continue
        if fence is not None or "|" not in line:
            continue
        row = line.removeprefix("|").removesuffix("|")
        cells = [cell.strip() for cell in row.split("|")]
        if all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            continue
        if cells[:2] in (["模型 ID", "推理等级"], ["模型 ID", "模式"]):
            continue
        if len(cells) not in (3, 4):
            failures.append(f"model table line {line_no}: expected 3 or 4 cells")
            continue
        pair = []
        for cell in cells[:2]:
            match = re.fullmatch(r"`([^`\s]+)`|([^`\s]+)", cell)
            if not match:
                failures.append(f"model table line {line_no}: invalid option cell {cell!r}")
                break
            pair.append(match.group(1) or match.group(2))
        if len(pair) == 2:
            options.append((pair[0], pair[1]))
    if fence is not None:
        failures.append("model reference: unclosed code fence")
    counts = Counter(options)
    for pair in sorted(counts.keys() - EXPECTED_OPTIONS):
        failures.append(f"unknown model option: {pair[0]}/{pair[1]}")
    for pair in sorted(EXPECTED_OPTIONS - counts.keys()):
        failures.append(f"missing model option: {pair[0]}/{pair[1]}")
    for pair, count in sorted(counts.items()):
        if count > 1:
            failures.append(f"duplicate model option: {pair[0]}/{pair[1]} ({count})")
    return len(options), failures


def audit_package(root: Path) -> dict:
    """Return a JSON-compatible report, including malformed/missing file errors."""
    root = root.resolve()
    failures: list[str] = []
    document_count = 0
    link_count = 0
    configurations: dict[str, object] = {}

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    def check_models(relative: str, value: object) -> None:
        pending, visited = [value], set()
        while pending:
            item = pending.pop()
            if isinstance(item, str):
                for model in sorted(set(re.findall(r"\bgpt-[a-z0-9]+(?:[.-][a-z0-9]+)*\b", item))):
                    if "sol" in model.split("-"):
                        require(model == "gpt-6.1-sol", f"{relative}: unsupported Sol model {model}")
            elif isinstance(item, (dict, list, tuple, set)) and id(item) not in visited:
                # YAML aliases can share or cycle through containers.
                visited.add(id(item))
                if isinstance(item, dict):
                    pending.extend(item.keys())
                    pending.extend(item.values())
                else:
                    pending.extend(item)

    def read(relative: str) -> str:
        path = root / relative
        try:
            if not path.resolve().is_relative_to(root):
                failures.append(f"{relative}: file escapes package")
                return ""
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError, RuntimeError) as error:
            failures.append(f"{relative}: {type(error).__name__}")
            return ""
        check_models(relative, text)
        return text

    def parsed(relative: str, text: str, parser) -> object:
        try:
            value = parser(text)
        except (ValueError, yaml.YAMLError, RecursionError) as error:
            failures.append(f"{relative}: invalid data ({type(error).__name__})")
            return {}
        check_models(relative, value)
        return value

    def configuration(relative: str) -> object:
        if relative not in configurations:
            configurations[relative] = parsed(relative, read(relative),
                                               CONFIG_PARSERS[Path(relative).suffix.lower()])
        return configurations[relative]

    def mapping(relative: str) -> dict:
        value = configuration(relative)
        if not isinstance(value, dict):
            failures.append(f"{relative}: expected mapping")
            return {}
        return value

    manifest = mapping(".codex-plugin/plugin.json")
    require(manifest.get("name") == "adaptive-task-router", "plugin identity differs")
    version = manifest.get("version", "")
    require(isinstance(version, str) and bool(re.fullmatch(
        r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?", version
    )), "invalid release version")
    require(manifest.get("skills") == "./skills/", "skills discovery path differs")
    require(not any(k in manifest for k in ("apps", "mcpServers")), "unexpected runtime dependency")

    marketplace = mapping(".agents/plugins/marketplace.json")
    require(marketplace.get("name") == "afd2-sol61", "local marketplace identity differs")
    entries = marketplace.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1 or not isinstance(entries[0], dict):
        failures.append("local marketplace must expose exactly this plugin")
    else:
        entry = entries[0]
        require(entry.get("name") == manifest.get("name"), "marketplace/plugin identity differs")
        require(entry.get("source") == {"source": "local", "path": "."},
                "local source must resolve to this complete package")
        require(entry.get("policy") == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "unexpected installation policy")
        require(entry.get("category") == "Productivity", "unexpected marketplace category")
    require(read("LICENSE").startswith("MIT License"), "missing MIT license")

    for name, implicit in (("route-task", False), ("suggest-task-routing", True)):
        ui = mapping(f"skills/{name}/agents/openai.yaml")
        policy, interface = ui.get("policy"), ui.get("interface")
        policy = policy if isinstance(policy, dict) else {}
        interface = interface if isinstance(interface, dict) else {}
        prompt, description = interface.get("default_prompt"), interface.get("short_description")
        require(policy.get("allow_implicit_invocation") is implicit, f"{name}: invocation policy")
        require(isinstance(prompt, str) and f"${name}" in prompt, f"{name}: default prompt invocation")
        require(isinstance(description, str) and 25 <= len(description) <= 64,
                f"{name}: UI description length")
        require((root / f"skills/{name}/SKILL.md").is_file(), f"{name}: missing SKILL.md")

    for path in sorted(root.rglob("*")):
        if ".git" in path.relative_to(root).parts:
            continue
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            try:
                if not path.resolve().is_relative_to(root):
                    failures.append(f"{rel}: file escapes package")
                    continue
            except (OSError, RuntimeError) as error:
                failures.append(f"{rel}: {type(error).__name__}")
                continue
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in CONFIG_PARSERS:
            configuration(rel)
            continue
        if suffix in UNSUPPORTED_CONFIG_SUFFIXES:
            failures.append(f"{rel}: unsupported configuration format")
            continue
        if suffix != ".md":
            continue
        text = read(rel)
        header_match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
        header = parsed(rel, header_match.group(1), yaml.safe_load) if header_match else {}
        if not rel.startswith("tests/fixtures/"):
            require(header_match is not None, f"{rel}: missing metadata")
            if header_match:
                try:
                    if not isinstance(header, dict):
                        raise ValueError("expected mapping")
                    governed = header.get("metadata", header)
                    if not isinstance(governed, dict):
                        raise ValueError("expected metadata mapping")
                    for key in ("status", "owner", "last_verified", "verified_commit", "applies_to"):
                        require(bool(governed.get(key)), f"{rel}: missing {key}")
                    if path.name == "SKILL.md":
                        require(header.get("name") == path.parent.name, f"{rel}: skill identity")
                        require(bool(header.get("description")), f"{rel}: missing description")
                except (ValueError, yaml.YAMLError):
                    failures.append(f"{rel}: invalid metadata")
                document_count += 1
        require("[TODO:" not in text and "[INSERT" not in text, f"{rel}: unfinished scaffold")
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            target = target.split("#", 1)[0].strip("<>")
            if not target or re.match(r"[a-zA-Z][\w+.-]*:", target):
                continue
            resolved = (path.parent / target).resolve()
            require(resolved.is_relative_to(root), f"{rel}: reference escapes package: {target}")
            require(resolved.exists(), f"{rel}: missing reference: {target}")
            link_count += 1

    count, model_failures = validate_model_options(read("skills/route-task/references/model-routing.md"))
    failures.extend(model_failures)
    return {"passed": not failures, "documents": document_count,
            "local_links": link_count, "model_options": count, "failures": failures}


def main() -> int:
    result = audit_package(ROOT)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
