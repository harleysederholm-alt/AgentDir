# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
