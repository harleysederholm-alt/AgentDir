"""Smoke test — kaikki uudet v4.1.0 moduulit."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from pathlib import Path

print("=" * 60)
print("AgentDir 4.1.0 — Smoke Test Suite")
print("=" * 60)

# 1. GraphRAG
print("\n[1/5] GraphRAG (EntityGraph)")
from workspace.rag import EntityGraph
eg = EntityGraph()
chunks = [
    {"name": "sandbox", "content": "SovereignSandbox kayttaa AST-parsintaa Python-koodin validointiin."},
    {"name": "pipeline", "content": "AgentDir Pipeline lukee Inbox-kansion ja kirjoittaa Outbox-kansioon."},
    {"name": "rag", "content": "RAG-muisti kayttaa ChromaDB-tietokantaa ja FAISS-indeksia."},
    {"name": "swarm", "content": "SwarmManager spawnaa agentteja. OmniNode hajauttaa laskennan."},
]
eg.build_from_chunks(chunks)
assert eg.graph is not None, "Graph ei rakentunut"
assert eg.graph.number_of_nodes() > 0, "Ei solmuja"
assert eg.graph.number_of_edges() > 0, "Ei kaaria"
docs = eg.query_neighbors("sandbox python", hops=2)
pr = eg.get_pagerank(5)
print(f"  Solmut: {eg.graph.number_of_nodes()}")
print(f"  Kaaret: {eg.graph.number_of_edges()}")
print(f"  Haku: {docs[:3]}")
print(f"  PageRank: {[e for e,_ in pr[:3]]}")
print("  -> PASS")

# 2. A-RAG Hierarchy
print("\n[2/5] A-RAG Hierarkia (HierarchicalIndex)")
from workspace.rag import HierarchicalIndex
hi = HierarchicalIndex()
count = hi.build(Path("wiki"))
assert len(hi.map_entries) > 0, "Map empty"
assert len(hi.rooms) > 0, "No rooms"
rooms = hi.navigate("sandbox", top_rooms=3)
print(f"  Map entries: {len(hi.map_entries)}")
print(f"  Rooms: {list(hi.rooms.keys())[:5]}")
print(f"  Total chunks: {len(hi.all_chunks)}")
print(f"  Navigate 'sandbox': {rooms}")
print("  -> PASS")

# 3. KnowledgeIndex (unified)
print("\n[3/5] KnowledgeIndex (GraphRAG + A-RAG + Keyword)")
from workspace.rag import KnowledgeIndex
idx = KnowledgeIndex(wiki_path="wiki")
n = idx.build()
assert n > 0, "Build failed"
results = idx.query("sandbox", top_k=3)
stats = idx.stats()
savings = idx.measure_token_savings("sandbox")
print(f"  Built: {n} chunks")
print(f"  GraphRAG: {stats.get('graphrag', {}).get('nodes', 0)} solmua")
print(f"  Hierarchy: {stats.get('hierarchy', {}).get('rooms', 0)} huonetta")
print(f"  Query results: {len(results)}")
for r in results:
    name = r.get("name", "?")
    score = r.get("score", 0)
    strat = r.get("strategy", "?")
    print(f"    {name} (score={score:.2f}, {strat})")
print(f"  Token savings: {savings.get('savings_pct', 0):.1f}%")
print("  -> PASS")

# 4. Health Monitor
print("\n[4/5] Health Monitor")
from health_monitor import HealthMonitor
hm = HealthMonitor(root_path=".", check_interval=999)
results = hm.run_check_now()
assert len(results) > 0, "No checks"
for r in results:
    d = r if isinstance(r, dict) else r.to_dict()
    print(f"  {d['component']}: {d['status']} — {d['message']}")
print(f"  Auto-fixes: {hm._fix_count}")
print(f"  Healthy: {hm.is_healthy()}")
print("  -> PASS")

# 5. WebDAV (availability check only — no wsgidav needed)
print("\n[5/5] WebDAV Server (availability)")
from webdav_server import AgentDirWebDAV
wd = AgentDirWebDAV(root_path=".")
status = wd.status()
print(f"  Available: {wd.is_available()}")
print(f"  Status: {status}")
if wd.is_available():
    print(f"  Mount instructions:\n{wd.get_mount_instructions()}")
print("  -> PASS (availability check)")

print("\n" + "=" * 60)
print("ALL 5 MODULES VERIFIED")
print("=" * 60)
