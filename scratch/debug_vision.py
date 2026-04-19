import sys
from pathlib import Path
# Lisätään projektin juuri polkuun
sys.path.append(str(Path.cwd()))

from agentdir.vision.ollama_vision import OllamaVisionProvider

provider = OllamaVisionProvider(model_id="llava")
# Käytetään misc-kansiossa olevaa kuvaa
image_path = "workspace/visuals/misc/vesilasi.png"
result = provider.detect_objects(image_path, "Mitä tässä kuvassa on?")
print("RAW RESULT FROM LLAVA:")
print(result)
