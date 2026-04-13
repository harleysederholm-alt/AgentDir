"""
prompt_manager.py — Lataa ja formatoi promptit .prompts/ kansion templaateista.
"""
from pathlib import Path
import logging

logger = logging.getLogger("agentdir.prompt_manager")

class PromptManager:
    def __init__(self, prompts_dir: str = ".prompts"):
        self.prompts_dir = Path(prompts_dir)
        
    def get_prompt(self, role: str, task_description: str, input_content: str) -> str:
        """
        Lataa roolin mukaisen template-tiedoston (.md) ja injektoi arvot.
        Esim. role="analyzer" -> lukee .prompts/analyzer.md
        """
        role_key = role.lower().strip()
        
        # Map some common roles to files if needed, or just use the lowercased role
        role_mapping = {
            "erikoisanalyytikko": "analyzer",
            "koodari": "coder",
            "auditoija": "auditor"
        }
        
        mapped_role = role_mapping.get(role_key, role_key)
        template_file = self.prompts_dir / f"{mapped_role}.md"
        
        if not template_file.exists():
            logger.debug(f"Prompt template {template_file} not found. Using default fallback.")
            return self._default_prompt(role, task_description, input_content)
        
        content = template_file.read_text(encoding="utf-8")
        content = content.replace("{{ task_description }}", task_description)
        content = content.replace("{{ input_content }}", input_content)
        return content
        
    def _default_prompt(self, role: str, task: str, inp: str) -> str:
        return f"Olet {role}. Noudata käyttäjän tehtävää tarkasti.\n\nTehtävä:\n{task}\n\nSyöte:\n{inp}"
