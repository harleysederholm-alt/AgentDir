import base64
import requests
import logging
from pathlib import Path

logger = logging.getLogger("agentdir.vision.ollama")

class OllamaVisionProvider:
    """Näkömalli-palvelu Ollaman kautta (esim. LLaVA tai Moondream)."""
    
    def __init__(self, model_id="llava", host="http://localhost:11434"):
        self.model_id = model_id
        self.host = host

    def detect_objects(self, image_path: str, query: str = "Describe this image in detail and identify objects.") -> str:
        """Analysoi kuva Ollaman API:lla."""
        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            url = f"{self.host}/api/generate"
            payload = {
                "model": self.model_id,
                "prompt": query,
                "stream": False,
                "images": [image_data]
            }

            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "❌ Ei vastausta Ollamalta.")

        except Exception as e:
            logger.error("Ollama Vision virhe: %s", e)
            return f"❌ Ollama Vision virhe: {str(e)}"
