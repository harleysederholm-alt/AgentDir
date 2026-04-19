"""
webdav_server.py — AgentDir WebDAV-palvelin (Z:-asema)
Tarjoaa Inbox/, Outbox/ ja wiki/ natiivina levyasemana.

Käyttö:
  Windows: net use Z: http://localhost:8081/
  macOS:   Finder → Go → Connect to Server → http://localhost:8081/
  Linux:   mount -t davfs http://localhost:8081/ /mnt/agentdir

Poistaa copy-paste -tarpeen selaimen ja työpöydän väliltä.
Integroituu AgentDir-serverin daemon-threadiin.
"""
from __future__ import annotations

import logging
import threading
from pathlib import Path

logger = logging.getLogger("agentdir.webdav")

# Valinnainen riippuvuus (graceful degradation)
_HAS_WSGIDAV = False
try:
    from wsgidav.wsgidav_app import WsgiDAVApp
    from wsgidav.fs_dav_provider import FilesystemProvider
    _HAS_WSGIDAV = True
except ImportError:
    pass

_HAS_CHEROOT = False
try:
    from cheroot import wsgi as cheroot_wsgi
    _HAS_CHEROOT = True
except ImportError:
    pass


class AgentDirWebDAV:
    """
    WebDAV-palvelin joka tarjoaa AgentDirin kansiot levyasemana.
    
    Kansiorakenne WebDAV:ssa:
      /Inbox/   → Pudota uusia tehtäviä
      /Outbox/  → Lue vastauksia
      /wiki/    → Tietopankki (Ground Truth / LTM)
      /memory/  → RAG-muisti
      /docs/    → Dokumentaatio
    """

    def __init__(
        self,
        root_path: str | Path,
        host: str = "127.0.0.1",
        port: int = 8081,
    ) -> None:
        self.root = Path(root_path).resolve()
        self.host = host
        self.port = port
        self._server = None
        self._thread: threading.Thread | None = None
        self._running = False

    def is_available(self) -> bool:
        """Onko WebDAV käytettävissä (wsgidav + cheroot asennettu)?"""
        return _HAS_WSGIDAV and _HAS_CHEROOT

    def start(self) -> bool:
        """
        Käynnistä WebDAV-palvelin daemon-threadina.
        Palauttaa True jos käynnistys onnistui.
        """
        if not self.is_available():
            logger.warning(
                "WebDAV ei saatavilla. Asenna: pip install wsgidav cheroot"
            )
            return False

        if self._running:
            logger.info("WebDAV jo käynnissä portissa %d", self.port)
            return True

        # Varmista kansiot
        for folder in ["Inbox", "Outbox", "wiki", "memory", "docs"]:
            (self.root / folder).mkdir(exist_ok=True)

        config = {
            "host": self.host,
            "port": self.port,
            "provider_mapping": {
                "/": FilesystemProvider(str(self.root)),
            },
            "verbose": 0,
            "logging": {
                "enable": True,
                "enable_loggers": [],
            },
            # Turvallisuus: vain localhost, ei autentikaatiota (lokaali kaytto)
            "simple_dc": {
                "user_mapping": {
                    "*": True,
                },
            },
            "http_authenticator": {
                "domain_controller": "wsgidav.dc.simple_dc.SimpleDomainController",
                "accept_basic": True,
                "accept_digest": False,
                "default_to_digest": False,
            },
            "dir_browser": {
                "enable": True,
                "response_trailer": (
                    "<p>AgentDir Sovereign Engine — WebDAV Interface</p>"
                ),
            },
        }

        try:
            app = WsgiDAVApp(config)
            self._server = cheroot_wsgi.Server(
                (self.host, self.port),
                app,
            )
            self._server.shutdown_timeout = 1

            self._thread = threading.Thread(
                target=self._run,
                name="webdav-server",
                daemon=True,
            )
            self._thread.start()
            self._running = True
            logger.info(
                "WebDAV kaynnistetty: http://%s:%d/ -> %s",
                self.host, self.port, self.root,
            )
            return True
        except Exception as e:
            logger.error("WebDAV käynnistys epäonnistui: %s", e)
            return False

    def _run(self) -> None:
        """Palvelimen pääsilmukka (daemon-thread)."""
        try:
            self._server.start()
        except Exception as e:
            if self._running:
                logger.error("WebDAV virhe: %s", e)
        finally:
            self._running = False

    def stop(self) -> None:
        """Sammuta WebDAV-palvelin."""
        if self._server and self._running:
            self._running = False
            try:
                self._server.stop()
            except Exception:
                pass
            logger.info("WebDAV sammutettu")

    def get_mount_instructions(self) -> str:
        """Palauta mount-ohjeet käyttöjärjestelmälle."""
        url = f"http://{self.host}:{self.port}/"
        unc = f"\\\\{self.host}@{self.port}\\DavWWWRoot"
        return (
            f"[WebDAV] AgentDir Virtuaalilevy\n"
            f"   URL: {url}\n\n"
            f"   Windows:  net use Z: {unc}\n"
            f"   macOS:    Finder > Go > Connect to Server > {url}\n"
            f"   Linux:    mount -t davfs {url} /mnt/agentdir\n"
        )

    def status(self) -> dict:
        return {
            "available": self.is_available(),
            "running": self._running,
            "url": f"http://{self.host}:{self.port}/" if self._running else None,
            "root": str(self.root),
        }
