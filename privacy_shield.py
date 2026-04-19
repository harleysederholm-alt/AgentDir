import re
import logging
from pathlib import Path

logger = logging.getLogger("agentdir.privacy")

class PrivacyShield:
    """
    Sovereign Privacy Shield - Estää pääsyn kriittisiin ja sensitiivisiin tietoihin.
    Tukee sekä tiedostonimiä, polkuja että sisältöön perustuvaa suodatusta.
    """

    # Kielletyt kansiot (Physical paths)
    BLACKLISTED_FOLDERS = {
        "AppData",
        "Local AppData",
        "Roaming",
        ".ssh",
        ".git",
        "node_modules",
        "Windows",
        "System32",
        "Cookies",
        "Local Storage",
        "Temp",
        "System Volume Information",
        "$Recycle.Bin",
    }

    # Kielletyt tiedostopäätteet
    DANGEROUS_EXTENSIONS = {
        ".exe", ".dll", ".bin", ".dat", ".sys", ".lnk", ".tmp",
        ".key", ".pem", ".p12", ".pfx", ".crt", ".db", ".sqlite"
    }

    # Kielletyt tiedostonimkuviot (Regex)
    SENSITIVE_PATTERNS = [
        re.compile(r".*\.env.*", re.I),
        re.compile(r".*password.*", re.I),
        re.compile(r".*salis.*", re.I),
        re.compile(r".*secret.*", re.I),
        re.compile(r".*salainen.*", re.I),
        re.compile(r".*sopimus.*", re.I),
        re.compile(r".*token.*", re.I),
        re.compile(r".*credential.*", re.I),
        re.compile(r".*pankki.*", re.I),
        re.compile(r".*bank.*", re.I),
        re.compile(r".*vero.*", re.I),
        re.compile(r".*tax.*", re.I),
        re.compile(r".*private.*", re.I),
        re.compile(r"ntuser\.dat.*", re.I),
        re.compile(r"desktop\.ini", re.I),
        re.compile(r"thumbs\.db", re.I),
    ]

    def __init__(self, config: dict = None):
        self.cfg = config or {}
        self.level = self.cfg.get("privacy_level", "standard")

    def is_safe_path(self, path: str | Path) -> bool:
        """
        Tarkistaa onko polku turvallinen lukea.
        Palauttaa True jos polku on turvallinen, muuten False.
        """
        p = Path(path)
        
        # 1. Tarkista mustalistatut kansiot polussa
        for part in p.parts:
            if part in self.BLACKLISTED_FOLDERS:
                logger.debug("Privacy Shield: Estetty kansio '%s' polussa %s", part, p)
                return False

        # 2. Tarkista tiedostopääte
        if p.suffix.lower() in self.DANGEROUS_EXTENSIONS:
            logger.debug("Privacy Shield: Estetty pääte '%s' tiedostossa %s", p.suffix, p)
            return False

        # 3. Tarkista sensitiiviset nimikuviot
        name = p.name
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern.match(name):
                logger.debug("Privacy Shield: Estetty pattern '%s' tiedostossa %s", pattern.pattern, p)
                return False

        return True

    def scrub_content(self, text: str) -> str:
        """
        (Valinnainen) Siivoaa tekstistä tunnistettuja salaisuuksia.
        Tässä versiossa vain tynkä, voidaan laajentaa myöhemmin.
        """
        # Esimerkki: piilota API-avaimet (hyvin karkea)
        # return re.sub(r'(api[_-]key|secret|token)[\s:=]+[a-zA-Z0-9_\-\.]{10,}', r'\1: [REDACTED]', text, flags=re.I)
        return text
