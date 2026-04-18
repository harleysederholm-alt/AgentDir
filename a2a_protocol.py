"""
a2a_protocol.py — External Agent-to-Agent (A2A) protocol scaffold.

This module is the *external* bridge layer. It is intentionally separate from
``workflows/hermes.py`` and ``workflows/openclaw.py`` — those are **internal**
cognition loops (iterative research and multi-stage deep analysis), not
network protocols.

Naming convention:
    * ``A2A_Protocol_Alpha``  — generic external swarm-sync envelope (this
      module). Spoken by AgentDir nodes to *any* compatible external agent
      (e.g. other AgentDir instances on a LAN, Claude Desktop via MCP,
      Cursor / Zed, future OpenClaw/Hermes-branded external agents).
    * ``External_Swarm_Sync`` — same thing, alternate alias used in docs.

What this ships today (honest scope):
    * A typed envelope (:class:`A2AMessage`) — ``protocol`` + ``kind`` +
      ``sender`` + ``task`` + ``metadata``.
    * A registry (:class:`A2AProtocolRegistry`) — pluggable adapters for
      named external endpoints.
    * A ``NoopAdapter`` — proves the contract without making network calls.
    * Zero hard dependencies beyond Python stdlib. Future adapters (HTTP,
      WebSocket, MCP) plug in as subclasses of :class:`A2AAdapter`.

What this does **not** do yet:
    * No production transport. The existing ``server.py`` ``POST /task``
      endpoint already accepts A2A messages from other AgentDir instances;
      this module will wrap that transport (and future ones) behind a
      common adapter interface — tracked in
      ``docs/04-Architecture/API_SYMBIOSIS.md``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol

logger = logging.getLogger("agentdir.a2a_protocol")

PROTOCOL_VERSION = "a2a-alpha/1.0"


@dataclass(frozen=True)
class A2AMessage:
    """Canonical envelope for an external agent-to-agent exchange.

    Attributes:
        protocol:     Protocol version string (e.g. ``"a2a-alpha/1.0"``).
        kind:         One of ``"task"``, ``"query"``, ``"handshake"``,
                      ``"ack"``. Adapters SHOULD reject unknown kinds.
        sender:       Free-form sender identifier (agent name / URI).
        task:         Human-readable payload (prompt, query, etc.).
        metadata:     Arbitrary key/value bag (priority, trace-id, model
                      hints, TTL, etc.).
        timestamp:    ISO-8601 UTC timestamp set at construction time.
    """

    kind: str
    sender: str
    task: str
    metadata: dict[str, Any] = field(default_factory=dict)
    protocol: str = PROTOCOL_VERSION
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol": self.protocol,
            "kind": self.kind,
            "sender": self.sender,
            "task": self.task,
            "metadata": dict(self.metadata),
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "A2AMessage":
        return cls(
            kind=str(data.get("kind", "task")),
            sender=str(data.get("sender", "unknown")),
            task=str(data.get("task", "")),
            metadata=dict(data.get("metadata", {}) or {}),
            protocol=str(data.get("protocol", PROTOCOL_VERSION)),
            timestamp=str(
                data.get("timestamp")
                or datetime.now(timezone.utc).isoformat()
            ),
        )


class A2AAdapter(Protocol):
    """Transport-agnostic adapter for a single external endpoint.

    Implementations (HTTP POST to AgentDir ``/task``, WebSocket swarm,
    MCP bridge, future OpenClaw / Hermes branded external agents) all
    conform to this surface so :class:`A2AProtocolRegistry` can route
    without caring about the wire format.
    """

    name: str

    def send(self, message: A2AMessage) -> dict[str, Any]:  # pragma: no cover
        ...


class NoopAdapter:
    """In-memory adapter used for tests and smoke checks.

    Records every message that passes through it so callers can assert the
    envelope shape without touching the network.
    """

    def __init__(self, name: str = "noop") -> None:
        self.name = name
        self.outbox: list[A2AMessage] = []

    def send(self, message: A2AMessage) -> dict[str, Any]:
        self.outbox.append(message)
        logger.info(
            "[A2A:%s] kind=%s sender=%s task=%.60s",
            self.name,
            message.kind,
            message.sender,
            message.task,
        )
        return {"status": "accepted", "adapter": self.name, "echo": message.to_dict()}


class A2AProtocolRegistry:
    """Holds named adapters and routes outbound messages to them.

    The registry does not implement retry / backoff yet — failing adapters
    raise to the caller. That is deliberate: policy (retry, circuit break,
    dead-letter) belongs in ``orchestrator.py``, not here.
    """

    def __init__(self) -> None:
        self._adapters: dict[str, A2AAdapter] = {}

    def register(self, adapter: A2AAdapter) -> None:
        if adapter.name in self._adapters:
            logger.warning("[A2A] overwriting adapter '%s'", adapter.name)
        self._adapters[adapter.name] = adapter

    def remove(self, name: str) -> None:
        self._adapters.pop(name, None)

    def list_adapters(self) -> list[str]:
        return sorted(self._adapters.keys())

    def send(self, target: str, message: A2AMessage) -> dict[str, Any]:
        if target not in self._adapters:
            raise KeyError(
                f"Unknown A2A adapter '{target}'. Registered: {self.list_adapters()}"
            )
        return self._adapters[target].send(message)


global_a2a_registry = A2AProtocolRegistry()
"""Process-wide registry. Modules can register adapters at import time.

Intentionally empty at construction — callers register the adapters they
actually have (server-backed HTTP, WebSocket swarm, MCP bridge). The core
engine runs without any external A2A endpoint configured.
"""
