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
  # tai yksi komento (CI:n tapaan):
  pip install -e ".[dev]"
  ```

- For full functionality (LLM + embeddings), install [Ollama](https://ollama.com) and pull the models referenced in `config.json`.

## Running tests

From the repository root (this directory, where `watcher.py` lives):

```bash
pytest tests/ -v
```

Quick local check (Ollama models + LLM/embedding reachability):

```bash
python verify_setup.py
```

Start the watcher without manually activating the venv: `.\run.ps1` (Windows) or `./run.sh` (Unix).

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

Shipped: **Web-UI** (`/ui/`), Inbox/Outbox + file view, **tehtävän lähetys** lomakkeella, **HTMX**-päivitys listoille (kun `AGENTDIR_UI_SECRET` ei ole käytössä), OpenAPI-linkit; valinnainen `AGENTDIR_UI_SECRET` + `X-AgentDir-Key` / lomake `agentdir_key`.

Shipped: **A2A**-kovennus: `a2a.cors_origins`, `a2a.api_token` / `AGENTDIR_API_SECRET` (`POST /task`, `POST /rag/query`).

Shipped: **plugins** (`plugins/*.py`) + `hooks`-tapahtumat (katso `plugins/README.md`).

Follow-up ideas:

- Session-pohjainen Web-UI-auth (HTMX + salainen UI samaan aikaan).
- Tiukempi CORS + API-token -tarina Docker / Compose -esimerkeissä.

Open an issue before large UI changes so we can align on scope.
