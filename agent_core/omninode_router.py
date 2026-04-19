import logging

logger = logging.getLogger("agentdir.omninode_router")

class OmniNodeRouter:
    """
    Distributed Pre-processing Engine (Mobiili-Ingest / OmniNode).
    
    Reitittää tehtävät vaaditun kognitiivisen kuorman mukaan. Pakottaa rutiinitehtävät
    (kuten skannaukset ja perusrefaktoroinnit) lokaalille mallille kustannusten ja latenssin
    minimoimiseksi, ja varaa raskaat abstraktit ongelmat pilviagentille tai IDE-tekoälylle.
    """
    def __init__(self):
        # Määritellään laitteisto- / malliresurssit
        self.local_model = "Gemma 4 (Mobile NPU)"
        self.ide_model = "Opus 4.6 (IDE Agent)"

    def route_task(self, task_type: str) -> str:
        """
        Palauttaa mallin nimen, jolle kyseinen tehtävätyyppi pitäisi ohjata.
        
        Args:
            task_type (str): Tehtävän luokittelu (esim. "Ingest", "Architecture Decision")
        
        Returns:
            str: Valitun mallin tunnus
        """
        logger.info(f"Määritetään reititystä tehtävätyypille: [{task_type}]")
        
        # Kevyt esikäsittely ja lokaalit skannaukset -> Mobiili-Ingest paradigma
        if task_type in ["Ingest", "Anchor Generation", "Routine Refactor"]:
            logger.info("-> Reititetään lokaalille NPU:lle (Mobiili-Ingest paradigma)")
            return self.local_model
            
        # Monimutkaiset riippuvuudet ja abstraktit päätökset -> Raskas IDE agentti
        elif task_type in ["Architecture Decision", "Complex Debug"]:
            logger.info("-> Reititetään raskaalle IDE-agentille (Syvällinen ongelmanratkaisu)")
            return self.ide_model
            
        else:
            # Oletuksena turvaudutaan paikalliseen perusmalliin
            logger.info("-> Tuntematon tehtävätyyppi, reititetään oletuksena lokaalille mallille")
            return self.local_model
