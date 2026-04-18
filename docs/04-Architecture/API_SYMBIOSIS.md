# API Symbiosis — Single Source of Truth for Web / Desktop / Mobile

> Frontends (Next.js `web/`, Tauri `desktop/`, PWA `/app`, CLI REPL) all
> hit the same backend endpoints. This document enumerates them so there
> is one surface to implement against — not three.

Backend entrypoints:

| Process              | File              | Default port | Purpose                             |
|----------------------|-------------------|--------------|-------------------------------------|
| A2A / Web-UI server  | `server.py`       | `8080`       | REST + Web-UI + MCP router          |
| OmniNode bridge      | `omninode.py`     | `8081`       | mDNS + WebSocket node sharding      |
| MCP subrouter        | `mcp_server.py`   | (mounted on 8080 at `/mcp`) | MCP tools (`rag_search`, `run_sandbox`) |

All endpoints speak JSON. Authentication is a shared static token
(`AGENTDIR_API_SECRET` env var or `a2a.api_token` in `config.json`) sent as
`X-AgentDir-Api-Key:` **or** `Authorization: Bearer …`. Endpoints that do
not require the token are noted explicitly.

---

## 1. Public (no auth)

These must remain open for health checks, service discovery, and
first-contact handshakes.

### `GET /status`

Liveness + build metadata.

```json
{
  "name": "AgentDir Engine",
  "role": "Älykäs tutkija ja prosessoija",
  "version": "4.0.0",
  "status": "online",
  "timestamp": "2026-04-18T06:52:00.000Z"
}
```

### `GET /manifest`

Returns `manifest.json` verbatim. Capability advertisement for A2A
discovery; mirrors `manifest.json` at repo root.

### `GET /discover`

Scans the local network for other AgentDir instances via mDNS
(`_agentdir._tcp.local.`). Returns:

```json
{ "agents": [{ "name": "SwarmPeer", "role": "analyst", "ip": "192.168.1.42", "port": 8080 }], "count": 1 }
```

### `GET /stats`

Evolution engine KPI snapshot (prompt version, success rate, total
tasks). Returns `{"error": "..."}` if evolution is disabled.

---

## 2. Authenticated

### `POST /task`

Queues a task from another agent into `Inbox/` as a Markdown file. The
local `watcher.py` then picks it up and runs it through
`orchestrator.py`.

Request:

```json
{ "task": "Summarise Q1 incident tickets", "from": "SwarmPeer", "priority": "normal" }
```

Response:

```json
{ "status": "accepted", "task_id": "20260418_065300_from_SwarmPeer", "message": "Tehtävä vastaanotettu ja lisätty jonoon" }
```

Rate limit: `a2a.rate_limit_per_minute` (default 60) per client IP. 429
on exceed.

### `POST /rag/query`

Direct semantic lookup against this agent's ChromaDB memory.

```json
{ "query": "EU AI Act audit requirements", "n_results": 3 }
```

Returns `{ "query": "...", "result": "..." }`.

---

## 3. MCP sub-router (`/mcp/v1`)

Standard Model Context Protocol surface so Claude Desktop, Cursor, Zed,
and any MCP-speaking client can use AgentDir as a tool provider.

### `GET /mcp/v1/tools`

Returns the list of callable tools with JSON-Schema descriptions:

* `rag_search { query, n_results? }` — query this node's RAG memory.
* `run_sandbox { code }` — execute Python in the AST / Windows Sandbox
  isolation layer.

### `POST /mcp/v1/tools/call`

```json
{ "name": "rag_search", "parameters": { "query": "...", "n_results": 3 } }
```

Responses follow the MCP `{ content: [{type, text}], isError }` shape.

---

## 4. OmniNode WebSocket (port `8081`)

Owned by `omninode.py`. Intended for *compute off-load*, not task
orchestration. Messages are `compute_request` / `compute_result`
envelopes with `task_id`, `model`, `prompt`. The PC node (Gemma 4 E4B)
and mobile node (Gemma 4 E2B) share this channel; the router picks the
destination based on task class — see
[OmniNode routing](#omninode-routing).

### OmniNode routing

`OmniNodeManager.execute_sharded_task(model, prompt, task_class=...)`
distinguishes two task classes:

| Class         | Target                    | Use case                                    |
|---------------|---------------------------|---------------------------------------------|
| `"heavy"`     | PC node (E4B / desktop)   | Full cognitive pipeline, sandboxed exec, synthesis |
| `"ingest"`    | Mobile node (E2B / PWA)   | Background anchoring, short classification, chat reply |

The router prefers a node whose role matches the requested class; if no
matching node is connected it falls back to the first available node
(legacy v4.0 behaviour).

---

## 5. External Agent-to-Agent (A2A) scaffold

`a2a_protocol.py` is the *outbound* side of the same surface. It defines
`A2AMessage` envelopes and a pluggable `A2AAdapter` contract so
AgentDir can talk to external swarms (other AgentDir instances, MCP
clients, future OpenClaw / Hermes branded *external* agents) without
hard-coding any single transport.

> **Not to be confused with** `workflows/hermes.py` and
> `workflows/openclaw.py` — those are *internal* cognition loops
> (iterative research and multi-stage deep analysis) that run inside
> `orchestrator.py`. They never touch the network.

See `a2a_protocol.py` docstring for the envelope schema.

---

## 6. Frontend wiring cheat-sheet

### Next.js `web/` (landing + PWA)

Base URL is configurable via `NEXT_PUBLIC_AGENTDIR_API`. For local dev:

```ts
const API = process.env.NEXT_PUBLIC_AGENTDIR_API ?? "http://localhost:8080";

await fetch(`${API}/status`);                                    // 1. status
await fetch(`${API}/rag/query`, {                                // 2. RAG
  method: "POST",
  headers: { "Content-Type": "application/json", "X-AgentDir-Api-Key": token },
  body: JSON.stringify({ query, n_results: 3 }),
});
```

### Tauri `desktop/`

Uses Rust-side `reqwest` + Tauri IPC to shield the API token from the
webview. `desktop/src-tauri/src/lib.rs` should load the token from OS
keychain via `keyring` crate.

### PWA `web/app/`

Same endpoints as landing, but stores the token in `localStorage`
behind a user-entered passphrase. The PWA never talks to the OmniNode
WebSocket directly — `server.py` proxies compute requests on its behalf.

### CLI `cli.py`

Speaks to `server.py` over the same HTTP surface when the engine is
running; otherwise it runs the pipeline in-process via
`orchestrator.WorkflowOrchestrator`.

---

## 7. Versioning

* Protocol version is published in `manifest.json` (`"protocol":
  "agentdir-a2a/1.0"`).
* External A2A envelopes carry `"protocol": "a2a-alpha/1.0"` — see
  `a2a_protocol.PROTOCOL_VERSION`.
* Breaking changes bump the major number and keep the previous router
  mounted at `/v{n-1}/` for one release cycle.
