import sys
import os

# Lisätään nykyinen hakemisto poluun
sys.path.append(os.getcwd())

from agentdir.vision.vision_manager import get_vision_manager

def test_vision():
    manager = get_vision_manager()
    image_path = r"c:\Users\harle\Projektit\Project AgentDir\agentdir\Workspace\visuals\objects\vesilasi_final.png"
    
    if not os.path.exists(image_path):
        print(f"Kuvaa ei löydy: {image_path}")
        return

    print(f"--- Aloitetaan analyysi: {image_path} ---")
    result = manager.analyze(image_path, "Tunnista kuvassa olevat esineet mahdollisimman tarkasti.")
    print("\n--- RAW VISION OUTPUT ---")
    print(result)
    print("--- END ---")

if __name__ == "__main__":
    test_vision()
