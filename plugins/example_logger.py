"""
Esimerkkilaajennus (Plugin) Sovereign Enginelle.
Tämä laajennus kuuntelee agentin keskeisiä elinkaaritapahtumia ja logittaa ne omaan lokitiedostoonsa.

Voit käyttää tätä pohjana omille yhteisölaajennuksillesi!
Asennus: Lisää tämä tiedosto `plugins/` -kansioon. Sovereign Engine lataa sen automaattisesti.
"""
import logging
from pathlib import Path

# Tuodaan hooks-rajapinta, jonka kautta tapahtumat rekisteröidään
import hooks

# Luodaan laajennukselle oma loggeri
logger = logging.getLogger("plugin.example_logger")
logger.setLevel(logging.INFO)

# Voidaan kirjoittaa myös erilliseen lokitiedostoon
plugin_log_path = Path("outputs/plugin_example.log")
if not plugin_log_path.parent.exists():
    plugin_log_path.parent.mkdir(parents=True)

fh = logging.FileHandler(plugin_log_path, encoding="utf-8")
fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(fh)


def on_before_task(task_id: str, payload: dict, **kwargs):
    """Kutsutaan ennen kuin agentti aloittaa tehtävän käsittelyn."""
    logger.info(f"🚀 Uusi tehtävä havaittu [{task_id}]: {payload.get('task', 'N/A')[:50]}...")


def on_agent_decision(task_id: str, decision: str, reasoning: str, **kwargs):
    """Kutsutaan kun agentti tekee päätöksen (esim. työkaluvirta, router)."""
    logger.info(f"🧠 Agentin päätös [{task_id}]: {decision}")
    logger.debug(f"   Perustelu: {reasoning}")


def on_after_parsed(path: Path, text: str, **kwargs):
    """Kutsutaan heti kun tiedosto on ilmestynyt Inboxiin ja luettu muistiin."""
    logger.info(f"📄 Tiedosto luettu Inboxista: {path.name} ({len(text)} merkkiä)")


# Rekisteröidään hook-kuuntelijat
hooks.register("before_task_process", on_before_task)
hooks.register("on_agent_decision", on_agent_decision)
hooks.register("after_file_parsed", on_after_parsed)

logger.info("✅ Example Logger -liitännäinen aktivoitu. Odotetaan tapahtumia...")
