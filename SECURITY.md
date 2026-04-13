# Security policy

## Reporting a vulnerability

Please report security issues **privately** instead of using public GitHub issues, so we can assess and fix them before wider disclosure.

1. Open a **private vulnerability report** via GitHub (Security tab → Advisories), if enabled for the repository, or  
2. Email the repository maintainers with subject line `[AgentDir security]` and include steps to reproduce and affected versions.

We aim to acknowledge reports within a few business days.

## Scope and expectations

- **No built-in OAuth2, user accounts, or enterprise SSO** — the Web-UI uses a shared secret (`AGENTDIR_UI_SECRET`) and optional session cookies; A2A uses an optional API token. For internet-facing deployments, put AgentDir behind a **reverse proxy** with TLS and, if needed, your own identity layer.
- AgentDir runs arbitrary **LLM-generated Python** in a subprocess with AST-based checks. This reduces risk for casual use but is **not a full sandbox** comparable to containers or kernel-level isolation. For untrusted inputs or production, run inside **Docker** (or a similar isolated environment) as described in the README.
- The default A2A server uses permissive CORS (`*`) when **no** A2A API token is configured, and is intended for **local or trusted networks**. When `AGENTDIR_API_SECRET` or `a2a.api_token` is set, wildcard CORS (`*`) is **rejected** (no cross-origin browser headers until you set explicit `a2a.cors_origins`). Do not expose the service to the public internet without TLS, authentication, and a reverse proxy.
- The bundled **Web-UI** (`/ui/`) lists and displays files under `Inbox/` and `Outbox/` only. Optionally set `AGENTDIR_UI_SECRET`. Browser HTML requests are redirected to **`/ui/login`** unless the client sends `X-AgentDir-Key` or has already authenticated via the signed session cookie **`agentdir_session`**. Set a strong, separate **`AGENTDIR_SESSION_SECRET`** (at least 16 characters) for cookie signing in production; alternatively use `ui.session_secret` in `config.json` if long enough, or the server derives a key from `AGENTDIR_UI_SECRET` when no dedicated session secret is provided. When users reach the UI over **HTTPS** (including via a TLS-terminating reverse proxy), set **`AGENTDIR_UI_COOKIE_SECURE=1`** or `ui.cookie_secure: true` so the session cookie is marked **Secure**; otherwise browsers may refuse to store it on HTTPS sites. HTMX partial requests without a valid session receive **`401`** with **`HX-Redirect`** to `/ui/login` so the dashboard can recover without a broken partial swap. **`POST /ui/login`** applies a per-IP in-memory rate limit on **failed** password attempts (default **5 per 10 minutes**; not shared across server processes). Successful logins are not blocked by the counter. **401** responses from protected UI routes are logged at **warning** with method, path, and client IP only (passwords and secrets are never logged). For HTML form uploads (`POST /ui/submit`), the same UI secret may be sent in the form field `agentdir_key` (weaker than a header-only flow; prefer local-only use or a reverse proxy with proper auth for anything beyond a trusted LAN). Full browser CSRF protection for those forms is not implemented; prefer network isolation or fronting with an auth-aware proxy for high-risk deployments.
- **A2A write endpoints** (`POST /task`, `POST /rag/query`): when `a2a.api_token` in `config.json` or `AGENTDIR_API_SECRET` in the environment is set, clients must send `X-AgentDir-Api-Key` or `Authorization: Bearer <token>`. Prefer the environment variable in production so the token is not stored in a file. Combine with a narrow `a2a.cors_origins` list instead of `*` before exposing the API beyond a trusted network.

Thank you for helping keep users safe.
