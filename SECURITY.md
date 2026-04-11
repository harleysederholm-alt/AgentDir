# Security policy

## Reporting a vulnerability

Please report security issues **privately** instead of using public GitHub issues, so we can assess and fix them before wider disclosure.

1. Open a **private vulnerability report** via GitHub (Security tab → Advisories), if enabled for the repository, or  
2. Email the repository maintainers with subject line `[AgentDir security]` and include steps to reproduce and affected versions.

We aim to acknowledge reports within a few business days.

## Scope and expectations

- AgentDir runs arbitrary **LLM-generated Python** in a subprocess with AST-based checks. This reduces risk for casual use but is **not a full sandbox** comparable to containers or kernel-level isolation. For untrusted inputs or production, run inside **Docker** (or a similar isolated environment) as described in the README.
- The default A2A server uses permissive CORS (`*`) and is intended for **local or trusted networks**. Do not expose it to the public internet without TLS, authentication, and a reverse proxy.

Thank you for helping keep users safe.
