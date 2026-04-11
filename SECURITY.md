# Security policy

## Reporting a vulnerability

Please report security issues **privately** instead of using public GitHub issues, so we can assess and fix them before wider disclosure.

1. Open a **private vulnerability report** via GitHub (Security tab → Advisories), if enabled for the repository, or  
2. Email the repository maintainers with subject line `[AgentDir security]` and include steps to reproduce and affected versions.

We aim to acknowledge reports within a few business days.

## Scope and expectations

- AgentDir runs arbitrary **LLM-generated Python** in a subprocess with AST-based checks. This reduces risk for casual use but is **not a full sandbox** comparable to containers or kernel-level isolation. For untrusted inputs or production, run inside **Docker** (or a similar isolated environment) as described in the README.
- The default A2A server uses permissive CORS (`*`) and is intended for **local or trusted networks**. Do not expose it to the public internet without TLS, authentication, and a reverse proxy.
- The bundled **Web-UI** (`/ui/`) lists and displays files under `Inbox/` and `Outbox/` only. Optionally set `AGENTDIR_UI_SECRET` and send `X-AgentDir-Key` so casual browsers cannot open the dashboard on a shared LAN without the secret. For HTML form uploads (`POST /ui/submit`), the same secret may be sent in the form field `agentdir_key` (weaker than a header-only flow; prefer local-only use or a reverse proxy with proper auth for anything beyond a trusted LAN).
- **A2A write endpoints** (`POST /task`, `POST /rag/query`): when `a2a.api_token` in `config.json` or `AGENTDIR_API_SECRET` in the environment is set, clients must send `X-AgentDir-Api-Key` or `Authorization: Bearer <token>`. Prefer the environment variable in production so the token is not stored in a file. Combine with a narrow `a2a.cors_origins` list instead of `*` before exposing the API beyond a trusted network.

Thank you for helping keep users safe.
