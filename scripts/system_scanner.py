import os
import logging
from pathlib import Path
from datetime import datetime
from privacy_shield import PrivacyShield

logger = logging.getLogger("agentdir.scanner")

class SystemScanner:
    """
    Sovereign System Scanner - Kartoittaa tiedostojärjestelmän "ison kuvan".
    Luo wiki/workspace_map.md tiedoston ja indeksoi löydökset RAG:iin.
    """

    def __init__(self, config: dict, root_path: Path):
        self.config = config.get("filesystem", {})
        self.root = root_path
        self.shield = PrivacyShield(config)
        self.depth_limit = self.config.get("depth_limit", 3)
        self.external_paths = self.config.get("external_paths", [])

    def scan_all(self, rag=None) -> str:
        """Suorittaa täyden skannauksen ja palauttaa MD-raportin."""
        logger.info("Aloitetaan järjestelmäskannaus (depth limit: %d)", self.depth_limit)
        
        report = []
        report.append(f"# Sovereign Workspace Map — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("\n## External Contexts\n")

        for path_str in self.external_paths:
            p = Path(os.path.expandvars(path_str)).expanduser()
            if not p.exists():
                logger.warning("Skannattavaa polkua ei löydy: %s", p)
                continue
                
            report.append(f"### {p.name} (`{p}`)\n")
            report.append("```text")
            tree = self._scan_recursive(p, 0, rag)
            report.append(tree)
            report.append("```\n")

        # Tallenna raportti wikiin
        wiki_dir = self.root / "wiki"
        wiki_dir.mkdir(exist_ok=True)
        map_path = wiki_dir / "workspace_map.md"
        map_path.write_text("\n".join(report), encoding="utf-8")
        
        logger.info("Skannaus valmis: %s", map_path)
        return "\n".join(report)

    def _scan_recursive(self, path: Path, depth: int, rag=None) -> str:
        """Käy kansiot läpi rekursiivisesti ja palauttaa tekstimuotoisen puun."""
        if depth > self.depth_limit:
            return "  " * depth + "... (depth limit reached)\n"

        if not self.shield.is_safe_path(path):
            return "  " * depth + f"[RESTRICTED] {path.name}\n"

        output = []
        try:
            # Listaa tiedostot ja kansiot
            items = sorted(list(path.iterdir()), key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for item in items:
                prefix = "  " * depth
                if not self.shield.is_safe_path(item):
                    continue

                if item.is_dir():
                    output.append(f"{prefix}📁 {item.name}/")
                    output.append(self._scan_recursive(item, depth + 1, rag))
                else:
                    output.append(f"{prefix}📄 {item.name}")
                    if rag:
                        # (Valinnainen) Index metadata to RAG
                        rag.add(
                            doc_id=f"scan_{item.absolute()}",
                            text=f"Tiedosto: {item.name} sijaitsee kohteessa {item.parent}",
                            metadata={"type": "os_scan", "path": str(item.absolute())}
                        )

        except PermissionError:
            output.append("  " * depth + "❌ [Permission Denied]")
        except Exception as e:
            logger.error("Virhe skannattaessa %s: %s", path, e)
            output.append("  " * depth + f"❌ [Error: {e}]")

        return "\n".join([line for line in output if line.strip()])
