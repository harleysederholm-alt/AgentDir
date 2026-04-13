"""
test_mcp_server.py — MCP Server -testit
Testaa /mcp/v1/tools ja /mcp/v1/tools/call -endpointit.
"""
import pytest
from unittest.mock import patch, MagicMock


def _get_test_client():
    """Luo FastAPI TestClient MCP-reittien kanssa."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from mcp_server import mcp_router

    app = FastAPI()
    app.include_router(mcp_router)
    return TestClient(app)


class TestMCPToolDiscovery:
    """Testaa, että MCP palauttaa oikeat työkalut."""

    def test_list_tools_returns_two_tools(self):
        client = _get_test_client()
        resp = client.get("/mcp/v1/tools")
        assert resp.status_code == 200
        data = resp.json()
        assert "tools" in data
        assert len(data["tools"]) == 2

    def test_list_tools_contains_rag_search(self):
        client = _get_test_client()
        resp = client.get("/mcp/v1/tools")
        names = [t["name"] for t in resp.json()["tools"]]
        assert "rag_search" in names

    def test_list_tools_contains_run_sandbox(self):
        client = _get_test_client()
        resp = client.get("/mcp/v1/tools")
        names = [t["name"] for t in resp.json()["tools"]]
        assert "run_sandbox" in names

    def test_tool_schemas_have_required_fields(self):
        client = _get_test_client()
        resp = client.get("/mcp/v1/tools")
        for tool in resp.json()["tools"]:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            assert tool["inputSchema"]["type"] == "object"


class TestMCPToolCall:
    """Testaa tool call -endpointtia."""

    def test_unknown_tool_returns_404(self):
        client = _get_test_client()
        resp = client.post("/mcp/v1/tools/call", json={
            "name": "nonexistent_tool",
            "parameters": {}
        })
        assert resp.status_code == 404

    @patch("rag_memory.RAGMemory")
    @patch("server.get_server_config")
    def test_rag_search_returns_content(self, mock_config, mock_rag_cls):
        mock_rag = MagicMock()
        mock_rag.query.return_value = "test RAG result"
        mock_rag_cls.return_value = mock_rag
        mock_config.return_value = {"rag": {"enabled": True}}

        client = _get_test_client()
        resp = client.post("/mcp/v1/tools/call", json={
            "name": "rag_search",
            "parameters": {"query": "tekoäly", "n_results": 2}
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["isError"] is False
        assert len(data["content"]) > 0

    @patch("sandbox_executor.execute")
    def test_sandbox_success(self, mock_exec):
        mock_exec.return_value = {"success": True, "output": "42"}

        client = _get_test_client()
        resp = client.post("/mcp/v1/tools/call", json={
            "name": "run_sandbox",
            "parameters": {"code": "print(42)"}
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["isError"] is False

    @patch("sandbox_executor.execute")
    def test_sandbox_failure_returns_error(self, mock_exec):
        mock_exec.return_value = {"success": False, "error": "SyntaxError"}

        client = _get_test_client()
        resp = client.post("/mcp/v1/tools/call", json={
            "name": "run_sandbox",
            "parameters": {"code": "invalid((("}
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["isError"] is True
