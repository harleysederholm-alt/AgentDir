import logging
import threading
import json
import sys
from pathlib import Path
import torch
from PIL import Image
from transformers import AutoModelForCausalLM

import os
import sys
from unittest.mock import MagicMock

# Pakotetaan torch toimimaan ilman dynaamista kääntämistä (cl.exe)
os.environ["TORCH_COMPILE_DISABLE"] = "1"
os.environ["TORCHDYNAMO_DISABLE"] = "1"

# Windows-yhteensopivuus: Huijataan modeling-tiedostoa, jos triton puuttuu
try:
    import triton
except ImportError:
    # Luodaan valevale-triton, jotta modeling_falcon_perception.py ei kaadu latauksessa
    mock_triton = MagicMock()
    sys.modules["triton"] = mock_triton
    sys.modules["triton.language"] = MagicMock()
    logger = logging.getLogger("agentdir.vision")
    logger.warning("Triton puuttuu. Käytetään MagicMock-valetritonia (Windows-yhteensopivuus).")

# Monkeypatch torch.compile: Estetään flex_attentionin paketointi kääntäjään
original_compile = torch.compile
def patched_compile(model, *args, **kwargs):
    # Jos yritetään kääntää flex_attentionia, palautetaan alkuperäinen funktio sellaisenaan
    if hasattr(model, "__name__") and "flex_attention" in model.__name__:
        return model
    return original_compile(model, *args, **kwargs)

torch.compile = patched_compile

logger = logging.getLogger("agentdir.vision")

# Polku tilatiedostolle (jaettu server.py:n kanssa)
STATUS_FILE = Path(__file__).resolve().parent / "status.json"

class FalconVisionProvider:
    """
    Falcon Perception -visiontuottaja asynkronisella latauksella ja tilan seurannalla.
    """
    
    def __init__(self, model_id="tiiuae/Falcon-Perception-300M"):
        self.model_id = model_id
        self._model = None
        self.status = "Idle"  # Idle, Loading, Ready, Error
        self._lock = threading.Lock()
        self._update_status_file()
        logger.info(f"FalconVisionProvider alustettu: {self.model_id}")

    def _update_status_file(self):
        """Tilaa hallinnoi nyt VisionManager (hybrid)."""
        pass

    def warm_up(self):
        """Käynnistää mallin latauksen taustalla."""
        with self._lock:
            if self.status != "Idle":
                return
            self.status = "Loading"
            self._update_status_file()
        
        thread = threading.Thread(target=self._load_model, daemon=True)
        thread.start()
        logger.info("Falcon Vision: Taustalataus käynnistetty.")

    def _load_model(self):
        try:
            logger.info(f"Ladataan Falcon-malli ({self.model_id})...")
            model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                trust_remote_code=True,
                device_map="auto",
                attn_implementation="eager" # Estetään Triton-pohjainen Flash Attention
            )
            with self._lock:
                self._model = model
                self.status = "Ready"
                self._update_status_file()
            logger.info("OK Falcon Vision: Malli ladattu ja valmis.")
        except Exception as e:
            logger.error(f"Error Falcon Vision: Latausvirhe: {e}")
            with self._lock:
                self.status = "Error"
                self._update_status_file()

    @property
    def model(self):
        with self._lock:
            if self.status == "Ready":
                return self._model
            return None

    def detect_objects(self, image_path: str, query: str = "objects") -> str:
        """
        Tunnistaa objektit kuvasta. Huomioi lataustilan.
        """
        if self.model is None:
            status = self.status
            msg = "Vision model is still warming up (EU AI Act Transparency: status={}). Please wait."
            logger.warning(msg.format(status))
            return msg.format(status)

        try:
            image = Image.open(image_path)
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            logger.info("Analysoidaan kuvaa: %s", image_path)
            with torch.no_grad():
                predictions = self.model.generate(image, query)[0]
            
            return str(predictions)
        except Exception as e:
            logger.error("Virhe Falcon-analyysissä: %s", e)
            return f"Error kuva-analyysissä: {str(e)}"

    def describe_scene(self, image_path: str) -> str:
        return self.detect_objects(image_path, query="Describe the scene in detail.")
