# Contributing to AgentDir

Thank you for your interest in improving AgentDir.

## Development setup

- Python **3.10 or newer** (3.11+ recommended for local development).
- Create a virtual environment and install dependencies:

  ```bash
  python -m venv .venv
  source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  pip install -r requirements-dev.txt
  ```

- For full functionality (LLM + embeddings), install [Ollama](https://ollama.com) and pull the models referenced in `config.json`.

## Running tests

From the repository root (this directory, where `watcher.py` lives):

```bash
pytest tests/ -v
```

All tests should pass before you open a pull request.

## Pull requests

- Keep changes focused on a single concern when possible.
- Update documentation if you change behaviour that users rely on (README, Docker, or config keys).
- Do not commit runtime data (`memory/`, `Inbox/` contents, `Outbox/` contents, `swarm/`); these are ignored by `.gitignore` except `.gitkeep` placeholders.

## Code style

- Match the style of existing modules (typing, logging, Finnish user-facing strings where already used).
- Prefer small, reviewable diffs over large refactors unless discussed first.

## More documentation

See [README.md](README.md) for architecture, configuration, and Docker usage.

## Roadmap (Phase 2)

Planned follow-up work (not required for Phase 1 contributions):

- Lightweight web UI for Inbox/Outbox status and task flow.
- Stricter authentication and CORS for deployments exposed to the internet (see README “Production / internet”).

If you want to work on Phase 2, open an issue first so we can agree on the approach (e.g. HTMX vs separate frontend).
