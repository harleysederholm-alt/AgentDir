import sys
import os
import asyncio

# Lisätään hakemisto poluun
sys.path.append(os.getcwd())

from agentdir.vision.vision_manager import get_vision_manager
from watcher import process_with_self_correction

def test_grounding():
    # Simuloidaan tilanne: LLaVA palauttaa sekavaa tekstiä
    vision_result = "[Provider: LLaVA Fallback] Näyttaa olevan kuvassa esineet, mikrofiisalustus, huoneessa on kakkukapusto."
    category = "objects"
    final_path = r"c:\Users\harle\Projektit\Project AgentDir\agentdir\Workspace\visuals\objects\vesilasi_final.png"

    # Uusi grounding prompt (kopioitu watcher.py:stä)
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

    print("--- Lähetetään uusi grounding prompt LLM:lle ---")
    
    # Huom: process_with_self_correction on jo määritelty watcher.py:ssä ja se käyttää LLM:ää
    result, success = process_with_self_correction(grounding_prompt, "test_fix_grounding.png")
    
    print("\n--- FINAL REPORT OUTPUT ---")
    print(result)
    print("--- END ---")

if __name__ == "__main__":
    test_grounding()
