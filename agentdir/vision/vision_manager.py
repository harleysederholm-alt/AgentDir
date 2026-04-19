import logging
import os
import json
import requests
import threading
import time
from .falcon_perception import FalconVisionProvider, STATUS_FILE
from .ollama_vision import OllamaVisionProvider

logger = logging.getLogger("agentdir.vision.manager")

class VisionManager:
    """Hallitsee visio-tarjoajia ja hoitaa fallback-logiikan sekä tilan raportoinnin."""
    
    def __init__(self):
        self.falcon = FalconVisionProvider()
        self.ollama = OllamaVisionProvider(model_id="llava")
        self.falcon_active = True
        self._last_status = "Idle"
        self.update_status()
        
        # Käynnistetään taustapäivitys
        self._stop_event = threading.Event()
        self._status_thread = threading.Thread(target=self._periodic_status_update, daemon=True)
        self._status_thread.start()

    def _periodic_status_update(self):
        """Päivittää tilan taustalla säännöllisesti."""
        while not self._stop_event.is_set():
            try:
                self.update_status()
            except Exception:
                pass
            time.sleep(10)

    def update_status(self) -> dict:
        """Päivittää ja palauttaa yhdistetyn tilatiedon."""
        falcon_status = self.falcon.status # Idle, Loading, Ready, Error
        
        # Tarkistetaan Ollama
        ollama_ok = False
        try:
            resp = requests.get(f"{self.ollama.host}/api/tags", timeout=1.5)
            if resp.status_code == 200:
                ollama_ok = True
        except Exception:
            ollama_ok = False

        # Määritetään kokonaistila
        if falcon_status == "Ready":
            unified = "Ready"
        elif falcon_status == "Loading":
            unified = "Hybrid" if ollama_ok else "Loading"
        elif ollama_ok:
            unified = "Fallback" # Falcon Idle/Error, mutta LLaVA toimii
        else:
            unified = falcon_status if falcon_status != "Idle" else "Offline"

        self._last_status = unified
        
        status_data = {
            "status": unified,
            "falcon": falcon_status,
            "ollama": "OK" if ollama_ok else "OFFLINE",
            "model": self.falcon.model_id if unified == "Ready" else "Hybrid/LLaVA"
        }

        # Päivitetään yhteinen tiedosto Dashboardia varten
        try:
            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(status_data, f)
        except Exception as e:
            logger.warning(f"VisionManager: Status-tiedoston päivitys epäonnistui: {e}")

        return status_data

    def analyze(self, image_path: str, query: str = "Tunnista kuvassa olevat esineet.") -> str:
        """Kokeilee ensin Falconia, sitten Ollamaa fallbackina."""
        status_info = self.update_status()
        
        # 1. Yritetään Falconia vain jos se on Ready
        if self.falcon_active and status_info.get("falcon") == "Ready":
            try:
                result = self.falcon.detect_objects(image_path, query)
                
                # Tarkistetaan ettei palautunut virhettä tai odotusviestiä
                is_warming_up = "warming up" in result.lower() or "loading" in result.lower()
                is_error = "error" in result.lower() or "cl is not found" in result.lower()

                if is_error or is_warming_up:
                    logger.warning(f"Falcon ei valmis tai palautti virheen: {result[:50]}... Vaihdetaan fallbackiin.")
                    # Jos se oli virhe, estetään Falcon hetkeksi. Jos Loading, annetaan yrittää ensi kerralla.
                    if is_error:
                        self.falcon_active = False 
                else:
                    return f"[Provider: Falcon] {result}"
            except Exception as e:
                logger.error("Falcon kriittinen virhe: %s. Siirrytään fallbackiin.", e)
                self.falcon_active = False
                self.update_status()

        # 2. Fallback: Ollama / LLaVA (Käytetään jos Falcon ei Ready tai epäonnistui)
        logger.info("Käytetään LLaVA-fallbackia (Ollama)...")
        try:
            result = self.ollama.detect_objects(image_path, query)
            return f"[Provider: LLaVA Fallback] {result}"
        except Exception as e:
            logger.error(f"Kriittinen virhe molemmissa visio-tarjoajissa: {e}")
            return f"Error: Visio-analyysi epäonnistui kaikilla tarjoajilla. ({e})"

    def detect_objects(self, image_path: str, query: str = "Tunnista kuvassa olevat esineet.") -> str:
        return self.analyze(image_path, query)

    def warm_up(self):
        """Alustaa Falconin taustalla."""
        if self.falcon_active:
            try:
                self.falcon.warm_up()
            except Exception:
                self.falcon_active = False
        self.update_status()

# Global singleton
_manager = None

def get_vision_manager():
    global _manager
    if _manager is None:
        _manager = VisionManager()
    return _manager
