"""Keep the connector's shared Pages and publication contracts explicit."""

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _workflow(name: str):
    return yaml.safe_load((ROOT / ".github/workflows" / name).read_text())


def _actions_on(workflow):
    # PyYAML's YAML 1.1 reader represents the Actions ``on`` key as True.
    return workflow["on"] if "on" in workflow else workflow[True]


def test_pages_publishes_spec_dashboard_and_supports_manual_refresh():

    config = json.loads((ROOT / ".config/spec-dashboard.json").read_text())
    assert config == {
        "version": 1,
        "sources": [{"glob": "specs/*/status.json", "kind": "spec"}],
    }


def test_legacy_docs_publisher_is_removed_and_release_flags_remain_canonical():
    assert not (ROOT / ".github/workflows/docs.yml").exists()


def test_development_skill_has_real_delivery_contract_and_actual_tests():
    skill = ROOT / "stirlingpdf_agent/skills/stirlingpdf-agent-development/SKILL.md"
    content = skill.read_text()

    assert "name: stirlingpdf-agent-development" in content
    assert "## Rapid delivery: the 5-minute contract" in content
    assert "tests/test_publication_workflow.py" in content
    assert "tests/test_read_only_status.py" in content
    assert "tests/test_fleet_name.py" in content
    assert "STIRLINGPDF_API_KEY" in content
