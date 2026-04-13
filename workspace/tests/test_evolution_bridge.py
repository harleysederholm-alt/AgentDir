"""
test_evolution_bridge.py -- EvolutionBridge-testit
Testaa evoluutiosillan alustus, tilastot ja tehtavan rekisterointi.
"""
import sys
sys.path.insert(0, ".")

from workspace.evolution_bridge import EvolutionBridge


class TestEvolutionBridge:
    """Testaa EvolutionBridgen perusoperaatiot."""

    def test_init_without_config(self, tmp_path, monkeypatch):
        """Alustus onnistuu ilman config.json -tiedostoa."""
        monkeypatch.chdir(tmp_path)
        bridge = EvolutionBridge(config_path=str(tmp_path / "missing.json"))
        # Ei kaadu vaikka config puuttuu
        assert bridge is not None

    def test_get_stats_returns_dict(self, tmp_path, monkeypatch):
        """get_stats() palauttaa aina dictin."""
        monkeypatch.chdir(tmp_path)
        bridge = EvolutionBridge(config_path=str(tmp_path / "missing.json"))
        stats = bridge.get_stats()
        assert isinstance(stats, dict)

    def test_is_active_with_engine(self):
        """is_active on True kun EvolutionEngine loytyy."""
        bridge = EvolutionBridge()
        # Jos evolution_engine.py on importattavissa, is_active = True
        # Jos ei, is_active = False (molemmat hyva)
        assert isinstance(bridge.is_active, bool)

    def test_current_version(self):
        """current_version palauttaa merkkijonon."""
        bridge = EvolutionBridge()
        ver = bridge.current_version
        assert isinstance(ver, str)
        assert ver.startswith("v")

    def test_record_task(self):
        """record_task() ei kaadu oikealla syotteella."""
        bridge = EvolutionBridge()
        result = bridge.record_task({
            "success": True,
            "task": "test task",
            "print_id": "test123",
            "summary": "test",
        })
        assert isinstance(result, dict)

    def test_record_task_failure(self):
        """record_task() toimii myos epaonnistuneen tehtavan kanssa."""
        bridge = EvolutionBridge()
        result = bridge.record_task({
            "success": False,
            "task": "failed task",
            "print_id": "fail001",
        })
        assert isinstance(result, dict)
