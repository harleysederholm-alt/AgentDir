"""
test_sandbox.py -- SovereignSandbox v2 testit
Testaa subprocess-suoritus (Docker vaatii Docker Daemonin).
"""
import sys
sys.path.insert(0, ".")

from workspace.sandbox import SovereignSandbox


class TestSovereignSandbox:
    """Testaa hiekkalaatikkosuorituksen perustapaukset."""

    def setup_method(self):
        # Pakota subprocess-moodi (Docker ei aina saatavilla)
        self.sb = SovereignSandbox(prefer_docker=False)

    def test_runs_safe_code(self):
        """Yksinkertainen print-komento onnistuu."""
        result = self.sb.execute("print('hello agentdir')")
        assert result["success"] is True
        assert "hello agentdir" in result["stdout"]

    def test_captures_output(self):
        """Laskenta ja tulostus tallentuvat stdouttiin."""
        result = self.sb.execute("x = sum(range(10)); print(x)")
        assert result["success"] is True
        assert "45" in result["stdout"]

    def test_catches_syntax_error(self):
        """Syntaksivirhe palauttaa success=False."""
        result = self.sb.execute("def broken(")
        assert result["success"] is False

    def test_catches_runtime_error(self):
        """Ajonaikainen virhe (ZeroDivision) palauttaa success=False."""
        result = self.sb.execute("print(1/0)")
        assert result["success"] is False
        assert "ZeroDivision" in result["stderr"]

    def test_timeout(self):
        """Timeout-mekanismi pysayttaa pitkan suorituksen."""
        result = self.sb.execute("import time; time.sleep(99)", timeout=1)
        assert result["success"] is False
        assert "TIMEOUT" in result["stderr"]

    def test_returns_returncode(self):
        """Onnistunut suoritus palauttaa returncode 0."""
        result = self.sb.execute("print('ok')")
        assert result["returncode"] == 0

    def test_sandbox_type_is_subprocess(self):
        """Sandbox-tyyppi on subprocess kun Docker ei ole kaytossa."""
        assert self.sb.sandbox_type == "subprocess"

    def test_result_contains_sandbox_type(self):
        """Tulos sisaltaa sandbox_type -kentan."""
        result = self.sb.execute("print(1)")
        assert "sandbox_type" in result
        assert result["sandbox_type"] == "subprocess"
