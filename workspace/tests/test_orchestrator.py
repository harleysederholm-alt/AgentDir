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

    def test_init_omninode(self):
        """omninode-moodi alustetaan oikein."""
        orch = WorkflowOrchestrator(mode="omninode")
        assert orch.mode == "omninode"

    def test_init_sovereign(self):
        """sovereign-moodi alustetaan oikein."""
        orch = WorkflowOrchestrator(mode="sovereign")
        assert orch.mode == "sovereign"

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
