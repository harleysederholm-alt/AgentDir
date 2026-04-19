import logging
import re
from typing import Optional
from llm_client import LLMClient

logger = logging.getLogger("agentdir.vision.architect")

class VisualArchitect:
    """
    Käyttää LLM:ää (Gemma 4) luokittelemaan kuvat visuaalisen analyysin perusteella.
    Toteuttaa 'Smart Filing' -logiikan: Kuva siirretään omaan kategoriaansa Workspace/visuals/ -alle.
    """
    
    CATEGORIES = ["documents", "architecture", "objects", "scenery", "tech", "misc"]

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        logger.info("VisualArchitect alustettu.")

    def classify(self, vision_description: str) -> str:
        """
        Päättää kategorian visuaalisen kuvauksen perusteella.
        Palauttaa kansion nimen (esim. 'documents').
        """
        if "⚡ Vision model is still warming up" in vision_description:
            return "misc"

        prompt = (
            f"Sinun tehtäväsi on luokitella kuva-analyysin tulos kategoriaan.\n\n"
            f"Kuvailu: {vision_description}\n\n"
            f"Sallitut kategoriat: {', '.join(self.CATEGORIES)}\n\n"
            "Valitse paras kategoria. Vastaa AINOASTAAN yhdellä sanalla (kategorian nimi)."
        )
        
        system = "Olet AgentDir Architect. Luokittelet visuaalista dataa tarkasti."
        
        try:
            # Käytetään LLMClientin complete() metodia
            response = self.llm.complete(prompt, system=system).lower().strip()
            
            # Puhdistetaan vastaus (jos mukana on pisteitä tai muuta)
            match = re.search(r'(' + '|'.join(self.CATEGORIES) + ')', response)
            if match:
                category = match.group(0)
                logger.info(f"Architect: Kuva luokiteltu kategoriaan: {category}")
                return category
            
            logger.warning(f"Architect: Epäselvä vastaus LLM:ltä: {response}. Fallback: misc")
            return "misc"
            
        except Exception as e:
            logger.error(f"Architect: Virhe luokittelussa: {e}")
            return "misc"
