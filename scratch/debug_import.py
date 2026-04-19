import sys
import os
sys.path.append(os.getcwd())
try:
    from omninode import global_omni_manager
    print("Import successful")
    print(global_omni_manager.get_network_health())
except Exception as e:
    print(f"Import failed: {e}")
