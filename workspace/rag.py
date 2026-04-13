"""
rag.py — FAISS + sentence-transformers semanttinen haku /wiki-kansiolle
Perustuu A-RAG (arXiv:2602.03442) hierarkkiseen hakuperiaatteeseen.

Strategia: FAISS embedding-haku ensisijaisena, keyword-fallback varmuutena.
Graceful degradation: jos FAISS/sentence-transformers ei saatavilla,
putoaa automaattisesti keyword-hakuun ilman virheitä.
"""
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

logger = logging.getLogger("agentdir.rag")

# ── Valinnainen FAISS-tuki (graceful degradation) ──────────────────────
_HAS_FAISS = False
_HAS_TRANSFORMERS = False

try:
    import numpy as np
    import faiss

    _HAS_FAISS = True
except ImportError:
    pass

try:
    from sentence_transformers import SentenceTransformer

    _HAS_TRANSFORMERS = True
except ImportError:
    pass


class KnowledgeIndex:
    """
    Indeksoi /wiki kansion ja tarjoaa semanttisen haun.
    A-RAG periaate: navigoi ankkureiden kautta ennen koodin lukemista.

    Hakustrategiat (automaattinen valinta):
      1. FAISS + sentence-transformers (paras, vaatii kirjastot)
      2. Keyword-haku (fallback, aina käytettävissä)
    """

    # Embedding-malli (monilingvaalinen, pieni muistijalanjälki)
    DEFAULT_MODEL = "all-MiniLM-L6-v2"
    CACHE_FILE = ".rag_cache.json"

    def __init__(self, wiki_path: str = "wiki", model_name: str = "") -> None:
        self.wiki = Path(wiki_path)
        self._index: dict[str, str] = {}  # Keyword-fallback
        self._chunks: list[dict] = []  # FAISS: [{name, content, chunk_idx}]
        self._faiss_index = None
        self._embedder = None
        self._model_name = model_name or self.DEFAULT_MODEL
        self._doc_hashes: dict[str, str] = {}  # Muutosten tunnistus

    # ── Build ────────────────────────────────────────────────────────────

    def build(self) -> int:
        """
        Indeksoi kaikki /wiki tiedostot.
        Käyttää FAISS-embeddingejä jos saatavilla, muuten keyword-indeksi.
        Palauttaa indeksoitujen dokumenttien/chunkkien lukumäärän.
        """
        self._index.clear()
        self._chunks.clear()
        if not self.wiki.exists():
            return 0

        # Lue kaikki markdown-tiedostot
        for f in sorted(self.wiki.glob("*.md")):
            try:
                content = f.read_text(encoding="utf-8")
                self._index[f.stem] = content

                # Chunk-jako FAISS:ia varten (512 merkin ikkunat, 64 overlap)
                chunks = self._chunk_text(content, chunk_size=512, overlap=64)
                for i, chunk in enumerate(chunks):
                    self._chunks.append({
                        "name": f.stem,
                        "content": chunk,
                        "chunk_idx": i,
                        "source": str(f),
                    })
            except Exception as e:
                logger.warning("Tiedoston %s lukeminen epaonnistui: %s", f, e)

        # Yritä FAISS-indeksin rakennus
        if _HAS_FAISS and _HAS_TRANSFORMERS and self._chunks:
            self._build_faiss()

        doc_count = len(self._chunks) if self._chunks else len(self._index)
        logger.info(
            "RAG-indeksi rakennettu: %d dokumenttia, %d chunkkia, FAISS=%s",
            len(self._index), len(self._chunks), self._faiss_index is not None,
        )
        return doc_count

    def _chunk_text(
        self, text: str, chunk_size: int = 512, overlap: int = 64
    ) -> list[str]:
        """Jaa teksti limittäisiin chunkkeihin semanttista hakua varten."""
        if len(text) <= chunk_size:
            return [text]
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    def _build_faiss(self) -> None:
        """Rakenna FAISS-indeksi embedding-vektoreista."""
        try:
            if self._embedder is None:
                logger.info("Ladataan embedding-mallia: %s", self._model_name)
                self._embedder = SentenceTransformer(self._model_name)

            texts = [c["content"] for c in self._chunks]
            embeddings = self._embedder.encode(
                texts, show_progress_bar=False, normalize_embeddings=True
            )
            embeddings = np.array(embeddings, dtype=np.float32)

            # IndexFlatIP = cosine similarity (koska normalize_embeddings=True)
            dim = embeddings.shape[1]
            self._faiss_index = faiss.IndexFlatIP(dim)
            self._faiss_index.add(embeddings)

            logger.info(
                "FAISS-indeksi rakennettu: %d vektoria, dim=%d",
                self._faiss_index.ntotal, dim,
            )
        except Exception as e:
            logger.error("FAISS-indeksin rakennus epaonnistui: %s", e)
            self._faiss_index = None

    # ── Query ────────────────────────────────────────────────────────────

    def query(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Semanttinen haku. Valitsee automaattisesti parhaan strategian:
          1. FAISS cosine-similarity (jos rakennettu)
          2. Keyword-overlap (fallback)

        Palauttaa listan: [{name, content, score, strategy}]
        """
        if self._faiss_index is not None and self._embedder is not None:
            return self._query_faiss(query, top_k)
        return self._query_keyword(query, top_k)

    def _query_faiss(self, query: str, top_k: int = 5) -> list[dict]:
        """FAISS cosine-similarity -haku."""
        try:
            q_embedding = self._embedder.encode(
                [query], normalize_embeddings=True
            )
            q_embedding = np.array(q_embedding, dtype=np.float32)

            k = min(top_k, self._faiss_index.ntotal)
            scores, indices = self._faiss_index.search(q_embedding, k)

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self._chunks):
                    continue
                chunk = self._chunks[idx]
                results.append({
                    "name": chunk["name"],
                    "content": chunk["content"][:500],
                    "score": float(score),
                    "chunk_idx": chunk["chunk_idx"],
                    "source": chunk.get("source", ""),
                    "strategy": "faiss",
                })
            return results
        except Exception as e:
            logger.warning("FAISS-haku epaonnistui, fallback keyword: %s", e)
            return self._query_keyword(query, top_k)

    def _query_keyword(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Keyword-overlap haku (fallback kun FAISS ei saatavilla).
        Laskee kysely- ja dokumenttitermien leikkausjoukon.
        """
        if not self._index:
            return []

        query_terms = set(query.lower().split())
        results: list[tuple[str, str, int]] = []

        for name, content in self._index.items():
            content_terms = set(content.lower().split())
            overlap = len(query_terms & content_terms)
            if overlap > 0:
                results.append((name, content, overlap))

        results.sort(key=lambda x: x[2], reverse=True)
        return [
            {
                "name": r[0],
                "content": r[1][:500],
                "score": float(r[2]),
                "strategy": "keyword",
            }
            for r in results[:top_k]
        ]

    # ── Utility ──────────────────────────────────────────────────────────

    def has_faiss(self) -> bool:
        """Onko FAISS-indeksi aktiivinen?"""
        return self._faiss_index is not None

    def stats(self) -> dict:
        """Palauta indeksin tilastot."""
        return {
            "documents": len(self._index),
            "chunks": len(self._chunks),
            "faiss_active": self.has_faiss(),
            "faiss_vectors": (
                self._faiss_index.ntotal if self._faiss_index else 0
            ),
            "model": self._model_name if self._embedder else "keyword-only",
        }
