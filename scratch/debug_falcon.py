import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))

import torch
from agentdir.vision.falcon_perception import FalconVisionProvider

try:
    print("Initializing Falcon...")
    provider = FalconVisionProvider()
    print("Falcon initialized. Analyzing image...")
    image_path = "workspace/visuals/misc/vesilasi.png"
    result = provider.detect_objects(image_path, "Mitä tässä kuvassa on?")
    print("FALCON RESULT:")
    print(result)
except Exception as e:
    print(f"FALCON FAILED WITH ERROR: {e}")
    import traceback
    traceback.print_exc()
