"""
win_sandbox_driver.py - OS-tason eristys Windows Sandboxilla

Generoi .wsb konfiguraatiotiedoston ja ajaa koodia turvallisesti
täysin puhtaassa ja eristetyssä Windows Sandbox -virtuaaliympäristössä.
Vaatii Windows 10/11 Pro/Enterprise -version ja aktivoituna olevan Sandbox-ominaisuuden.
"""

import os
import tempfile
import subprocess
import logging

logger = logging.getLogger("agentdir.win_sandbox")

class WindowsSandboxDriver:
    def __init__(self, mapped_folder: str = None):
        self.mapped_folder = mapped_folder or os.getcwd()

    def generate_wsb(self, script_path: str, wsb_path: str):
        """Luo .wsb tiedoston Windows Sandboxin ohjaukseen."""
        wsb_content = f"""<Configuration>
  <MappedFolders>
    <MappedFolder>
      <HostFolder>{self.mapped_folder}</HostFolder>
      <SandboxFolder>C:\\AgentDirWorkspace</SandboxFolder>
      <ReadOnly>false</ReadOnly>
    </MappedFolder>
  </MappedFolders>
  <LogonCommand>
    <Command>cmd /c python C:\\AgentDirWorkspace\\{os.path.basename(script_path)} > C:\\AgentDirWorkspace\\sandbox_output.txt 2>&1</Command>
  </LogonCommand>
</Configuration>"""
        with open(wsb_path, "w", encoding="utf-8") as f:
            f.write(wsb_content)
            
    def run_isolated(self, code: str) -> dict:
        """Suorittaa koodin täysin eristetyssä Windows Sandboxissa."""
        logger.info("[WinSandbox] Aloitetaan eristetty suoritus...")
        try:
            script_path = os.path.join(self.mapped_folder, "sandbox_task.py")
            wsb_path = os.path.join(self.mapped_folder, "run.wsb")
            out_path = os.path.join(self.mapped_folder, "sandbox_output.txt")
            
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            self.generate_wsb(script_path, wsb_path)
            
            logger.info(f"[WinSandbox] Ajetaan: {wsb_path}")
            # Käynnistää eristetyn ympäristön
            subprocess.run(["cmd.exe", "/c", "start", "/wait", wsb_path], timeout=120)
            
            res = "Sandbox suoritus valmis. (Tulostetta ei luotu)"
            if os.path.exists(out_path):
                with open(out_path, "r", encoding="utf-8", errors="replace") as f:
                    res = f.read()
                    
            # Cleanup
            for p in [script_path, wsb_path, out_path]:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except:
                        pass
                        
            return {"success": True, "output": res, "error": ""}
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "", "error": "Sandbox timeout."}
        except Exception as e:
            logger.error(f"[WinSandbox] Virhe: {e}")
            return {"success": False, "output": "", "error": str(e)}
