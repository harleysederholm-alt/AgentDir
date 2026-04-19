"""
model_router.py — Mallireititin
Valitsee oikean LLM-backendin tehtävätyypin mukaan.
Tukee: Ollama, LM Studio, OpenAI-yhteensopivat.
"""
from __future__ import annotations

import os

# Tehtävätyypin mukaan valittu malli
TASK_ROUTING: dict[str, str] = {
    "code": "ollama/gemma4:e4b",
    "analysis": "ollama/gemma4:e4b",
    "vision": "ollama/llava",
    "summary": "ollama/gemma4:e4b",
    "default": os.getenv("AGENTDIR_DEFAULT_MODEL", "ollama/gemma4:e4b"),
}


class ModelRouter:
    """
    Valitsee tehtävälle sopivan LLM-backendin ja kutsuu sitä.
    """

    def select(self, task: str) -> str:
        """Valitse malli tehtävän sisällön perusteella."""
        task_lower = task.lower()
        if any(w in task_lower for w in ["korjaa", "koodi", "fix", "refactor", "debug"]):
            return TASK_ROUTING["code"]
        if any(w in task_lower for w in ["kuva", "näyttö", "image", "screenshot"]):
            return TASK_ROUTING["vision"]
        if any(w in task_lower for w in ["analysoi", "tutki", "compare", "analyze"]):
            return TASK_ROUTING["analysis"]
        if any(w in task_lower for w in ["tiivistä", "summary", "yhteenveto"]):
            return TASK_ROUTING["summary"]
        return TASK_ROUTING["default"]

    def call(self, model: str, prompt: str, context: str = "") -> str:
        """
        Kutsu mallia Ollama-yhteensopivalla API:lla.
        Fallback: mock-vastaus jos openai-kirjastoa ei ole asennettu.
        """
        try:
            from openai import OpenAI

            host_env = os.getenv("OLLAMA_HOST")
            if not host_env or host_env == "0.0.0.0":
                base_url = "http://localhost:11434/v1"
            elif not host_env.startswith("http"):
                base_url = f"http://{host_env}:11434/v1"
            else:
                base_url = host_env
            client = OpenAI(base_url=base_url, api_key="ollama")
            model_name = model.replace("ollama/", "")

            messages: list[dict[str, str]] = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})

            resp = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=2000,
            )
            return resp.choices[0].message.content or ""

        except ImportError as e:
            # Vaatii live-openai-kirjaston ollamaa varten
            print("![ERROR] LLM-rajapinnan käyttö vaatii 'openai' kirjaston asennuksen. Aja: pip install openai")
            raise e
        except Exception as e:
            # Auto-fallback OOM/RAM limits (OmniNode simulaatio tai kevyempi malli)
            if "memory" in str(e).lower() or "oom" in str(e).lower():
                print(f"[OMNINODE] {model} vaatii liikaa muistia. Aktivoidaan RAM Sharding ja reititetään kevyemmälle verkolle (llama3.2:3b)...")
                try:
                    resp = client.chat.completions.create(
                        model="llama3.2:3b",
                        messages=messages,
                        max_tokens=2000,
                    )
                    return resp.choices[0].message.content or ""
                except Exception as fallback_e:
                    return f"[ERROR] Fallback-mallikutsu epäonnistui: {fallback_e}"
            return f"[ERROR] Mallikutsu epäonnistui: {e}"
