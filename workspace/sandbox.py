"""
sandbox.py — Safe YOLO -hiekkalaatikko (SovereignSandbox v2)
Kaikki agenttien kirjoittama koodi ajetaan tassa.

Strategia (automaattinen valinta):
  1. Docker-kontti (--network none, read-only, mem limit) — paras eristys
  2. Subprocess (minimiymparisto, timeout) — fallback jos Docker ei saatavilla

Molemmat tarjoavat saman API:n: execute(code) -> {success, stdout, stderr}
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger("agentdir.sandbox")


class SovereignSandbox:
    """
    Eristetty suoritusymparisto agenttien koodille.

    Valitsee automaattisesti parhaan eristystavan:
      - Docker: taysi eristys (ei verkkoa, muistiraja, prosessiraja)
      - Subprocess: kevyt eristys (minimiymparisto, timeout)
    """

    DEFAULT_TIMEOUT = 30  # sekuntia
    DOCKER_IMAGE = "agentdir-sandbox"
    DOCKER_MEM_LIMIT = "256m"
    DOCKER_CPU_LIMIT = "0.5"

    def __init__(self, prefer_docker: bool = True) -> None:
        self._docker_available = False
        if prefer_docker:
            self._docker_available = self._check_docker()
        if self._docker_available:
            logger.info("Sandbox: Docker-moodi (taysi eristys)")
        else:
            logger.info("Sandbox: Subprocess-moodi (kevyt eristys)")

    def _check_docker(self) -> bool:
        """Tarkista onko Docker saatavilla ja image olemassa."""
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode != 0:
                return False
            # Tarkista onko sandbox-image olemassa
            result = subprocess.run(
                ["docker", "images", "-q", self.DOCKER_IMAGE],
                capture_output=True, text=True, timeout=5,
            )
            # Jos image loytyy, kayta sita; muuten subprocess
            return bool(result.stdout.strip())
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    # ── Julkinen API ─────────────────────────────────────────────────────

    def execute(self, code: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
        """
        Aja Python-koodi eristetyssa ymparistossa.

        Args:
            code: Ajettava Python-koodi merkkijonona
            timeout: Maksimiaika sekunteina

        Returns:
            dict: {success, stdout, stderr, returncode, sandbox_type}
        """
        if self._docker_available:
            return self._execute_docker(code, timeout)
        return self._execute_subprocess(code, timeout)

    # ── Docker-suoritus ──────────────────────────────────────────────────

    def _execute_docker(self, code: str, timeout: int) -> dict:
        """
        Aja koodi Docker-kontissa taydella eristyksella:
          - --network none     (ei verkkoyhteyksia)
          - --read-only        (ei kirjoituksia tiedostojarjestelmaan)
          - --memory 256m      (muistiraja)
          - --cpus 0.5         (CPU-raja)
          - --pids-limit 30    (prosessiraja, fork-pommi suoja)
          - --tmpfs /tmp:100M  (valikaikaistiedostot RAM-levylla)
        """
        try:
            result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "--network", "none",
                    "--read-only",
                    "--memory", self.DOCKER_MEM_LIMIT,
                    "--cpus", self.DOCKER_CPU_LIMIT,
                    "--pids-limit", "30",
                    "--tmpfs", "/tmp:size=50M",
                    "--security-opt", "no-new-privileges",
                    self.DOCKER_IMAGE,
                    "python", "-c", code,
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "sandbox_type": "docker",
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"TIMEOUT ({timeout}s) [docker]",
                "returncode": -1,
                "sandbox_type": "docker",
            }
        except Exception as e:
            logger.warning("Docker-suoritus epaonnistui, fallback subprocess: %s", e)
            return self._execute_subprocess(code, timeout)

    # ── Subprocess-suoritus (fallback) ───────────────────────────────────

    def _execute_subprocess(self, code: str, timeout: int) -> dict:
        """Aja koodi subprocess-eristyksessa minimiymparistolla."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                ["python", tmp_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                env={"PATH": os.environ.get("PATH", "")},
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "sandbox_type": "subprocess",
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"TIMEOUT ({timeout}s)",
                "returncode": -1,
                "sandbox_type": "subprocess",
            }
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    # ── Utility ──────────────────────────────────────────────────────────

    @property
    def sandbox_type(self) -> str:
        """Palauta aktiivinen sandbox-tyyppi."""
        return "docker" if self._docker_available else "subprocess"

    def build_docker_image(self) -> bool:
        """
        Rakenna sandbox Docker-image inline (ei vaadi Dockerfile.sovereign).
        Minimaalinen Python-image ilman verkkotyokaluja.
        """
        dockerfile_content = (
            "FROM python:3.12-slim\n"
            "RUN apt-get purge -y curl wget && apt-get autoremove -y\n"
            "WORKDIR /sandbox\n"
            'ENTRYPOINT ["python"]\n'
        )
        try:
            result = subprocess.run(
                ["docker", "build", "-t", self.DOCKER_IMAGE, "-"],
                input=dockerfile_content,
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                self._docker_available = True
                logger.info("Docker sandbox image rakennettu")
                return True
            logger.error("Docker build epaonnistui: %s", result.stderr)
            return False
        except Exception as e:
            logger.error("Docker build epaonnistui: %s", e)
            return False
