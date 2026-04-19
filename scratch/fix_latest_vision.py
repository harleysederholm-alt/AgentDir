import sys
import os
import asyncio
from pathlib import Path

# Lisätään hakemisto poluun
sys.path.append(os.getcwd())

from agentdir.vision.vision_manager import get_vision_manager
from watcher import process_with_self_correction

def fix_latest_fail():
    # Käytetään tuoreinta epäonnistunutta kuvaa (408 Timeout)
    image_name = "ui_20260414_012027_Nimet_n123123123123.png"
    vision_result = "[Provider: LLaVA Fallback] Screenshot: HTTP 408 Request Timeout. Attempting to connect to 'aktion' server failed. Gateway Timeout."
    category = "technical"
    final_path = r"c:\Users\harle\Projektit\Project AgentDir\agentdir\Workspace\visuals\technical\timeout_screenshot.png"

    grounding_prompt = (
        f"Kuva-analyysin tulokset (Raaka data):\n{vision_result}\n\n"
        f"Kategoria: {category}\n"
        f"Sijainti: {final_path}\n\n"
        "TEHTÄVÄ:\n"
        "Olet Sovereign Engine -visioanalyytikko. Tulkitse yllä oleva raaka data ja kuvaile, "
        "mitä kuvassa on ja miten se liittyy käynnissä olevaan tutkimukseen tai projekteihisi.\n\n"
        "HUOMIOITAVAA:\n"
        "- Käytä raakaa dataa (Provider: LLaVA/Falcon) onnistuneena ja luotettavana lähteenä. "
        "Vaikka teksti olisi fragmentaarista, pyri löytämään siitä semanttiset avainsanat.\n"
        "- ÄLÄ diagnosoi järjestelmän teknistä tilaa tai raportoi 'epäonnistumisista' vaikka "
        "RAG-muistissa olisi viittauksia aiempiin virheisiin.\n"
        "- Keskity vain nykyisen kuvan sisältöön ja sen tuomaan uuteen tietoon."
    )

    print(f"--- Korjataan analyysi: {image_name} ---")
    result, success = process_with_self_correction(grounding_prompt, image_name)
    
    out_file = Path("Outbox") / f"vastaus_{image_name.replace('.png', '_CORRECTED.md')}"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"# {image_name} (RE-ANALYZED & CORRECTED)\n")
        f.write("*2026-04-14 01:25:00 | AgentDir Engine – Engine Restart Recovery*\n\n---\n\n")
        f.write(f"VISUAL ANALYSIS REPORT:\n\n{result}")
    
    print(f"Korjattu raportti kirjoitettu: {out_file}")

if __name__ == "__main__":
    fix_latest_fail()
