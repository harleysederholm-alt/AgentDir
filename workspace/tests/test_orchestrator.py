"""
test_orchestrator.py — WorkflowOrchestrator-testit
Testaa orkestroijan alustus, policy gate ja pipeline.
"""
import sys
sys.path.insert(0, ".")

import pytest
from orchestrator import WorkflowOrchestrator


class TestWorkflowOrchestrator:
    """Testaa orkestroijan perustoiminnallisuus."""

    def test_init_openclaw(self):
        """openclaw-moodi alustetaan oikein."""
        orch = WorkflowOrchestrator(mode="openclaw")
        assert orch.mode == "openclaw"

    def test_init_hermes(self):
        """hermes-moodi alustetaan oikein."""
        orch = WorkflowOrchestrator(mode="hermes")
        assert orch.mode == "hermes"

    def test_invalid_mode_raises(self):
        """Tuntematon moodi nostaa virheen."""
        with pytest.raises(ValueError):
            WorkflowOrchestrator(mode="invalid")

    def test_policy_blocks_dangerous_task(self):
        """Policy gate estää vaarallisen tehtävän ennen suoritusta."""
        orch = WorkflowOrchestrator()
        result = orch.run("rm -rf /")
        assert result["success"] is False
        assert "Policy gate" in result["summary"]

    def test_run_returns_dict(self):
        """run() palauttaa aina dictin jossa on vaaditut avaimet."""
        orch = WorkflowOrchestrator()
        result = orch.run("analysoi tämä testi")
        assert isinstance(result, dict)
        assert "success" in result
        assert "summary" in result
        assert "model" in result
        assert "mode" in result
        assert "print_id" in result
