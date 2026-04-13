"""
test_rag.py -- KnowledgeIndex-testit (FAISS + keyword)
Testaa indeksointi, keyword-haku, chunking ja graceful degradation.
"""
import sys
sys.path.insert(0, ".")

from workspace.rag import KnowledgeIndex


class TestKnowledgeIndex:
    """Testaa RAG-haun perusoperaatiot."""

    def test_build_and_query(self, tmp_path):
        """Indeksointi ja haku palauttavat oikeat tulokset."""
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        (wiki / "auth.md").write_text(
            "JWT token authentication timeout 24h UTC", encoding="utf-8"
        )
        (wiki / "policy.md").write_text(
            "kaikki koodi tarkistetaan sandboxissa", encoding="utf-8"
        )

        idx = KnowledgeIndex(str(wiki))
        count = idx.build()
        assert count >= 2  # Dokumentteja tai chunkkeja

        results = idx.query("JWT token")
        assert len(results) > 0
        assert "auth" in results[0]["name"]

    def test_empty_wiki(self, tmp_path):
        """Tyhja wiki palauttaa tyhjan tuloslistan."""
        wiki = tmp_path / "wiki"
        wiki.mkdir()

        idx = KnowledgeIndex(str(wiki))
        count = idx.build()
        assert count == 0
        assert idx.query("anything") == []

    def test_query_with_no_match(self, tmp_path):
        """Haku jolla ei osumia palauttaa tyhjan listan."""
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        (wiki / "test.md").write_text("hello world", encoding="utf-8")

        idx = KnowledgeIndex(str(wiki))
        idx.build()
        results = idx.query("zzzzzzzzzzz")
        assert results == []

    def test_top_k_limits_results(self, tmp_path):
        """top_k rajoittaa palautettujen tulosten maaraa."""
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        for i in range(10):
            (wiki / f"doc_{i}.md").write_text(
                f"sisalto aiheesta data tiedosto {i}", encoding="utf-8"
            )

        idx = KnowledgeIndex(str(wiki))
        idx.build()
        results = idx.query("data tiedosto", top_k=3)
        assert len(results) <= 3

    def test_chunking(self, tmp_path):
        """Testaa etta pitkaa dokumentit pilkotaan chunkkeihin."""
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        # Luo 2000-merkkinen dokumentti (ylittaa 512-chunk rajan)
        long_content = "tama on testisisaltoa " * 100
        (wiki / "long.md").write_text(long_content, encoding="utf-8")

        idx = KnowledgeIndex(str(wiki))
        count = idx.build()
        # Pitaisi olla enemman chunkkeja kuin dokumentteja
        assert len(idx._chunks) > 1

    def test_stats(self, tmp_path):
        """stats() palauttaa oikean rakenteen."""
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        (wiki / "stats_test.md").write_text("testi", encoding="utf-8")

        idx = KnowledgeIndex(str(wiki))
        idx.build()
        stats = idx.stats()
        assert "documents" in stats
        assert "chunks" in stats
        assert "faiss_active" in stats
        assert stats["documents"] == 1

    def test_query_returns_strategy(self, tmp_path):
        """Tuloksissa on strategy-kentta."""
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        (wiki / "strat.md").write_text("keyword haku toimii", encoding="utf-8")

        idx = KnowledgeIndex(str(wiki))
        idx.build()
        results = idx.query("keyword haku")
        assert len(results) > 0
        assert "strategy" in results[0]
