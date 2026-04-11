# AgentDir v1.0 – Dockerfile
# Multi-stage build: pienempi lopullinen image

# ── Vaihe 1: Riippuvuudet ──────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Järjestelmäriippuvuudet (chromadb tarvitsee gcc:n)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Vaihe 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Kopioi asennetut paketit builderista
COPY --from=builder /install /usr/local

# Kopioi lähdekoodi
COPY *.py ./
COPY config.json manifest.json ./

# Luo tarvittavat kansiot
RUN mkdir -p Inbox Outbox memory plugins swarm

# Volume: agenttikansio mountataan ulkoa
VOLUME /agentdir

# Vaihda työkansio agenttikansioon
WORKDIR /agentdir

# Kopioi skriptit agenttikansioon käynnistyksessä
COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
CMD ["watcher"]
