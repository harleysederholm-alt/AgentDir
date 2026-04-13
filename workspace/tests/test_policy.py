"""
test_policy.py — PolicyEngine-testit
Testaa että EU AI Act Art.13 -portti estää oikeat asiat.
"""
import sys
sys.path.insert(0, ".")

import pytest
from workspace.policy import PolicyEngine


class TestPolicyEngine:
    """Testaa PolicyEnginen estot ja sallitut tehtävät."""

    def setup_method(self):
        self.policy = PolicyEngine()

    def test_allows_safe_analysis_task(self):
        """Normaali analyysitehtävä pitää päästä läpi."""
        assert self.policy.validate("analysoi data.csv ja tee raportti") is True

    def test_allows_normal_text(self):
        """Tavallinen teksti ei laukaise porttia."""
        assert self.policy.validate("kirjoita yhteenveto projektista") is True

    def test_blocks_rm_rf(self):
        """rm -rf pitää estää riippumatta kontekstista."""
        with pytest.raises(PermissionError) as exc_info:
            self.policy.validate("rm -rf /home/user")
        assert "rm -rf" in str(exc_info.value)

    def test_blocks_format_c(self):
        """format c: pitää estää."""
        with pytest.raises(PermissionError):
            self.policy.validate("format c: kaikki tiedostot pois")

    def test_blocks_eval(self):
        """eval() pitää estää."""
        with pytest.raises(PermissionError):
            self.policy.validate("käytä eval( tätä koodia")

    def test_blocks_even_in_innocent_context(self):
        """Kielletty kuvio estetään vaikka muuten teksti on viaton."""
        with pytest.raises(PermissionError):
            self.policy.validate(
                "kirjoita dokumentaatio: 'voit käyttää os.remove poistoon'"
            )

    def test_empty_task_raises_valueerror(self):
        """Tyhjä tehtävä ei ole sallittu."""
        with pytest.raises(ValueError):
            self.policy.validate("")

    def test_whitespace_only_raises_valueerror(self):
        """Pelkkä whitespace ei ole sallittu."""
        with pytest.raises(ValueError):
            self.policy.validate("   ")
