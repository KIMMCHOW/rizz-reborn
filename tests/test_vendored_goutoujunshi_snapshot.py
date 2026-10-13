"""
tests/test_vendored_goutoujunshi_snapshot.py
验证 vendor/goutoujunshi 快照完整、未被本地改动，并且仍然通过上游自检。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "vendor" / "goutoujunshi"
VALIDATOR = SKILL_DIR / "scripts" / "validate_skill.py"

REQUIRED_PATHS = (
    "SKILL.md",
    "UPSTREAM_SOURCE.md",
    "LICENSE",
    "agents/openai.yaml",
    "scripts/memory_store.py",
    "scripts/validate_skill.py",
    "references/knowledge/17-中国法律安全与危机转介.md",
    "references/knowledge/20-经典社交体系的机制、证据与风险边界.md",
    "references/practical/实战话术编排器：从一句回复到后续分支.md",
    "references/practical/长期记忆与关系档案.md",
)


def _run_validator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_vendored_snapshot_inventory_present() -> None:
    missing = [rel for rel in REQUIRED_PATHS if not (SKILL_DIR / rel).is_file()]
    assert missing == []


def test_vendored_snapshot_has_no_nested_git_directory() -> None:
    nested = [path for path in SKILL_DIR.rglob(".git") if path.is_dir()]
    assert nested == []


def test_skill_frontmatter_declares_upstream_name() -> None:
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert content.startswith("---\n")
    frontmatter = content.split("---", 2)[1]
    assert "\nname: goutoujunshi\n" in frontmatter


def test_project_declares_goutoujunshi_priority_layer() -> None:
    root_skill = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "docs/agent/SKILL_INTEGRATION.md" in root_skill
    integration = REPO_ROOT / "docs" / "agent" / "SKILL_INTEGRATION.md"
    assert integration.is_file()
    assert "狗头军师权重更高" in integration.read_text(encoding="utf-8")


def test_upstream_validator_passes() -> None:
    result = _run_validator()
    assert result.returncode == 0, result.stdout + result.stderr


def test_upstream_validator_passes_in_runtime_mode() -> None:
    result = _run_validator("--runtime")
    assert result.returncode == 0, result.stdout + result.stderr
