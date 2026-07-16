#!/usr/bin/env python3
"""Validate published AnyAPI skills and their canonical source relationship."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"
EXTERNAL_SKILL = ROOT / "skills" / "anyapi" / "SKILL.md"
CANONICAL_URL = "https://getanyapi.com/agent-onboarding/SKILL.md"

LEGACY_PATTERNS = {
    "credit-derived catalog price": re.compile(r"\b(?:from|perItem)Credits\b", re.IGNORECASE),
    "flat price alias": re.compile(r"\bpriceUsd\b", re.IGNORECASE),
    "ranked browse query": re.compile(r"/(?:catalog|v1/apis)\?[^\s`]*query", re.IGNORECASE),
    "list_apis query argument": re.compile(r"list_apis[^\n]*(?:query|\bq\b)", re.IGNORECASE),
    "credit-shaped public key": re.compile(r"[\"'`]\w*credit\w*[\"'`]\s*:", re.IGNORECASE),
}


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        fail(f"cannot read {path.relative_to(ROOT)}: {error}")
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def split_frontmatter(path: Path, content: str) -> tuple[str, str]:
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        fail(f"{path.relative_to(ROOT)} is missing YAML frontmatter")
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        fail(f"{path.relative_to(ROOT)} has unterminated YAML frontmatter")
    return "".join(lines[1:end]), "".join(lines[end + 1 :])


def check_frontmatter(path: Path, content: str) -> None:
    frontmatter, _ = split_frontmatter(path, content)
    for key in ("name", "description"):
        if not re.search(rf"(?m)^{key}:\s*\S", frontmatter):
            fail(f"{path.relative_to(ROOT)} frontmatter is missing {key}")


def manifest_skill_paths() -> list[Path]:
    plugin = load_json(PLUGIN_MANIFEST)
    marketplace = load_json(MARKETPLACE_MANIFEST)
    plugin_version = plugin.get("version")
    metadata = marketplace.get("metadata")
    marketplace_version = metadata.get("version") if isinstance(metadata, dict) else None
    if plugin_version != marketplace_version:
        fail("plugin and marketplace versions must match")

    skills = plugin.get("skills")
    if not isinstance(skills, list) or not skills:
        fail("plugin manifest must list at least one skill")

    paths: list[Path] = []
    for raw_path in skills:
        if not isinstance(raw_path, str):
            fail("plugin manifest skill paths must be strings")
        path = (ROOT / raw_path).resolve()
        try:
            path.relative_to(ROOT)
        except ValueError:
            fail(f"manifest skill path escapes the repository: {raw_path}")
        skill_file = path / "SKILL.md"
        if not path.is_dir() or not skill_file.is_file():
            fail(f"manifest-listed skill does not exist: {raw_path}/SKILL.md")
        paths.append(skill_file)
    return paths


def load_canonical_skill() -> str:
    local_path = os.environ.get("ANYAPI_CANONICAL_SKILL_PATH")
    if local_path:
        try:
            return Path(local_path).read_text()
        except OSError as error:
            fail(f"cannot read ANYAPI_CANONICAL_SKILL_PATH: {error}")

    request = Request(CANONICAL_URL, headers={"User-Agent": "anyapi-skills-check/1"})
    try:
        with urlopen(request, timeout=20) as response:
            return response.read().decode("utf-8")
    except (OSError, UnicodeError, URLError) as error:
        fail(
            f"cannot fetch canonical skill body from {CANONICAL_URL}: {error}; "
            "set ANYAPI_CANONICAL_SKILL_PATH for an offline checkout"
        )


def main() -> None:
    skill_files = manifest_skill_paths()
    all_skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if not all_skill_files:
        fail("skills directory contains no SKILL.md files")
    for path in all_skill_files:
        content = path.read_text()
        check_frontmatter(path, content)
        for label, pattern in LEGACY_PATTERNS.items():
            if pattern.search(content):
                fail(f"{path.relative_to(ROOT)} contains {label}")

    external_content = EXTERNAL_SKILL.read_text()
    canonical_content = load_canonical_skill()
    _, external_body = split_frontmatter(EXTERNAL_SKILL, external_content)
    _, canonical_body = split_frontmatter(ROOT / "canonical" / "SKILL.md", canonical_content)
    if external_body != canonical_body:
        fail(
            "skills/anyapi/SKILL.md body differs from the live machine skill; "
            "update getanyapi-com/anyapi/src/lib/agentSkill.ts first, deploy it, then sync this file"
        )

    print(f"skills checks passed ({len(skill_files)} manifest-listed skill)")


if __name__ == "__main__":
    main()
