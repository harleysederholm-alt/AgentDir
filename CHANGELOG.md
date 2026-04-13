# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.0.0] - 2026-04-13

### Added

- **Plugin API (Yhteisölaajennukset)** — Täysi tuki laajennuksille `plugins/` kansiossa.
  - Uudet hookit: `before_task_process`, `on_agent_decision`, `on_evolution_proposal`, `after_file_parsed`, `after_task_completed`.
  - Mukana tulee esimerkkiliitännäinen `plugins/example_logger.py`.
  - CLI `plugins` komento listaa aktiiviset laajennukset.
- **Tauri Binäärijakelu (Desktop)** — Tuotantovalmis `Sovereign Engine` GUI-paketointi.
  - `build_release.ps1` automatisoi koko asennuspaketin rakentamisen `.exe` asennusohjelmaksi ja yhdistää backend-skriptit levitettävään muotoon.
- **Test Suite v2** — 3 uutta testimoduulia kattamaan MCP Serverin, Hermes/OpenClaw -työnkulut ja CLI REPLin ympäristön.
- **Docker Hub Valmius** — Tuotantovalmis `Dockerfile.sovereign` varustettuna `HEALTHCHECK`, optimoiduilla `LABEL` -tageilla ja `VOLUME` mounteilla.

### Changed

- **`pyproject.toml`** — Version `1.1.0` → `3.5.1-alpha`, added 7 missing modules to `py-modules`.
- **`requirements.txt`** — Header updated to `Sovereign Engine 3.5.1`.
- **`launch_sovereign.ps1`** — Removed broken `openclaw gateway` reference; CLI now runs directly in current terminal.

### Fixed

- CLI `help` command now shows `hermes` and `openclaw` options.
- Logo version updated to `3.5.1`.

---

## [3.5.1-alpha] - 2026-04-13

### Added

- **QUICKSTART.md** — Simplified 3-minute onboarding guide for new users.
- **MCP Server** (`mcp_server.py`) — Stdio/SSE-compatible Model Context Protocol server exposing RAG search and sandbox execution to external AI tools (Claude, Cursor, etc.).
- **OmniNode** (`omninode.py`) — Distributed compute node using mDNS/Zeroconf for LAN-based inference offloading.
- **Windows Sandbox Driver** (`sandbox/win_sandbox_driver.py`) — OS-level code isolation using Microsoft Windows Sandbox (.wsb) for untrusted code execution.
- **Hermes Workflow** (`workflows/hermes.py`) — Iterative autonomous research workflow that cycles until a conclusion is reached.
- **OpenClaw Workflow** (`workflows/openclaw.py`) — Deep analysis pipeline combining RAG context with multi-step reasoning.
- **PromptManager** (`prompt_manager.py`) — Dynamic, role-based prompt template system replacing hardcoded strings.
- **Role Prompts** (`.prompts/`) — Modular prompt templates: `coder.md`, `analyzer.md`, `auditor.md`.
- **Evolution Guardrails** — `require_approval: true` (default) prevents autonomous prompt drift; proposals saved to `Outbox/EVOLUTION_PROPOSAL_vX.md` for human review.
- **Benchmark CI** (`.github/workflows/benchmark.yml`) — Automated performance testing pipeline.
- **Roadmap section** in README showing project progression from v3.0 → v4.0.
- **External review badge** — Independent 8.4/10 technical review documented in README.

### Changed

- **README.md** — Simplified header, added Quick Start link, expanded Mermaid architecture diagram with MCP/OmniNode/Hermes/Win Sandbox nodes, added Roadmap table.
- **Mermaid Architecture** — Now shows 6 subsystems: UI (incl. MCP), Pipeline, Nervous System, Cognition (Hermes + OpenClaw), Execution (AST + Win Sandbox), and Network (OmniNode).
- **SOVEREIGN_DASHBOARD.md** — Updated to v3.5.1-alpha with 13 monitored components.
- **Swarm Manager** — Now supports dynamic model injection and subprocess-based child agent spawning.
- **Watcher** — Integrated PromptManager for dynamic, context-aware prompt generation.
- **Server** — MCP router integrated into FastAPI application.
- Fixed all `YOUR_GITHUB_USER` placeholder URLs → real `harleysederholm-alt/AgentDir` links.

### Security

- Evolution engine now defaults to human-in-the-loop approval (`require_approval: true`), addressing AI Act compliance and preventing unsupervised prompt drift.
- Windows Sandbox provides full OS-level isolation for untrusted code, complementing existing AST-based analysis.

## [Unreleased]

### Added

- Web-UI session login (`/ui/login`), signed cookie `agentdir_session`, optional `AGENTDIR_SESSION_SECRET` / `ui.session_secret`.
- HTMX unauthenticated responses: `401` with `HX-Redirect` to login for smoother recovery when the session expires.
- Optional secure session cookie: `AGENTDIR_UI_COOKIE_SECURE` and `ui.cookie_secure` in `config.json`.
- Per-IP in-memory rate limiting for failed `POST /ui/login` attempts (5 per 10 minutes by default; see [SECURITY.md](SECURITY.md)).
- `docker-compose.secure.yml` + `.env.secure.example` for injecting secrets via Compose.
- Integration tests in `tests/test_server_ui.py` for full `server.app` Web-UI behaviour.

### Changed

- `SessionMiddleware` is registered from `register_ui()` so test apps and production share the same session setup.
- Web-UI failed login rate limit: **5 attempts per IP per 10 minutes** (was looser); **401** from protected UI routes logged at warning (method, path, IP only).
- When **A2A API token** is configured (`AGENTDIR_API_SECRET` or `a2a.api_token`), **`a2a.cors_origins` must not use `*`** — server disables CORS reflection until explicit origins are set.

### Security

- Session data is cleared on successful login before setting the UI-authenticated flag, reducing session-fixation risk for cookie-based sessions.
- `GET /status` remains unauthenticated for health checks; documented with CORS + token interaction.
