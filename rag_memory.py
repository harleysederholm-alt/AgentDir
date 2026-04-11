"""
AgentDir – RAG Memory Module
Paikallinen semanttinen muisti ChromaDB:llä + Ollama-embeddingillä.

KORJAUKSET alkuperäiseen verrattuna:
- Config ei ole globaali muuttuja vaan parametri → ei import-ongelmia
- Ollama /api/embed palautusrakenne korjattu ({"embeddings": [[...]]})
- Graceful fallback jos embedding-malli ei ole saatavilla (käyttää ChromaDB:n default-embeddingejä)
- Kaikki virheet kiinni → ei koskaan kaadu koko watcheria
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger("agentdir.rag")


class OllamaEmbedder:
    """Ollama-embedding-adaptori. Korjattu API-vastauksenkäsittely."""

    def __init__(self, endpoint: str, model: str):
        self.endpoint = endpoint
        self.model = model
        self._available: bool | None = None

    def is_available(self) -> bool:
        if self._available is None:
            try:
                resp = requests.post(
                    self.endpoint,
                    json={"model": self.model, "input": ["test"]},
                    timeout=10,
                )
                self._available = resp.status_code == 200
            except Exception:
                self._available = False
            if not self._available:
                logger.warning(
                    "Ollama embedding-malli '%s' ei saatavilla → käytetään ChromaDB default-embeddingejä",
                    self.model,
                )
        return self._available

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Palauttaa embeddings-listan. Ollama /api/embed → {'embeddings': [[float, ...]]}"""
        resp = requests.post(
            self.endpoint,
            json={"model": self.model, "input": texts},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()

        # Ollama palauttaa {"embeddings": [[...]]} – taulukko taulukoita
        raw = data.get("embeddings", [])
        if not raw:
            raise ValueError(f"Tyhjä embeddings-vastaus Ollamalta: {data}")
        return raw  # already list[list[float]]


class RAGMemory:
    """
    Paikallinen semanttinen muisti.
    - Tallentaa tehtävät + vastaukset vektori-DB:hen
    - Hakee semanttisesti samankaltaisia aiempia tehtäviä
    - Fallback: ChromaDB:n oma embedding jos Ollama ei ole käytössä
    """

    def __init__(self, config: dict, memory_path: str = "memory"):
        try:
            import chromadb
            from chromadb.utils import embedding_functions as ef
        except ImportError:
            raise RuntimeError("Asenna chromadb: pip install chromadb")

        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(exist_ok=True)

        emb_cfg = config.get("embedding", {})
        self.embedder = OllamaEmbedder(
            endpoint=emb_cfg.get("endpoint", "http://localhost:11434/api/embed"),
            model=emb_cfg.get("model", "mxbai-embed-large"),
        )

        self.client = chromadb.PersistentClient(path=str(self.memory_path / "chroma"))

        if self.embedder.is_available():
            # Käytetään Ollama-embeddingejä (paras laatu)
            embedding_fn = self._make_ollama_ef()
            logger.info("RAG: Käytetään Ollama-embeddingejä (%s)", emb_cfg.get("model"))
        else:
            # Fallback: ChromaDB:n oma default (sentence-transformers)
            embedding_fn = ef.DefaultEmbeddingFunction()
            logger.info("RAG: Käytetään ChromaDB default-embeddingejä (Ollama ei saatavilla)")

        self.collection = self.client.get_or_create_collection(
            name="agent_memory",
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def _make_ollama_ef(self):
        """Luo ChromaDB-yhteensopiva embedding function Ollamalle."""
        from chromadb import EmbeddingFunction, Embeddings

        embedder = self.embedder

        class _OllamaEF(EmbeddingFunction):
            def __call__(self, input: list[str]) -> Embeddings:
                return embedder.embed(input)

        return _OllamaEF()

    def add(self, doc_id: str, text: str, metadata: dict[str, Any]) -> None:
        """Lisää dokumentti muistiin. Päivittää jos sama id jo olemassa."""
        try:
            # Truncate jotta ei ylitetä embedding-mallin kontekstirajaa
            truncated = text[:8000]
            # Muutetaan kaikki metadata-arvot merkkijonoiksi (ChromaDB-vaatimus)
            safe_meta = {k: str(v) for k, v in metadata.items()}
            self.collection.upsert(
                documents=[truncated],
                metadatas=[safe_meta],
                ids=[doc_id],
            )
        except Exception as e:
            logger.error("RAG add epäonnistui: %s", e)

    def query(self, query_text: str, n_results: int = 3) -> str:
        """Hakee semanttisesti samankaltaiset muistit. Palauttaa tekstin."""
        try:
            count = self.collection.count()
            if count == 0:
                return "Ei aiempaa kontekstia."
            actual_n = min(n_results, count)
            results = self.collection.query(
                query_texts=[query_text[:2000]],
                n_results=actual_n,
            )
            docs = results.get("documents", [[]])[0]
            if not docs:
                return "Ei relevanttia aiempaa kontekstia."
            return "\n\n---\n\n".join(docs)
        except Exception as e:
            logger.error("RAG query epäonnistui: %s", e)
            return "RAG-haku epäonnistui."

    def count(self) -> int:
        try:
            return self.collection.count()
        except Exception:
            return 0
