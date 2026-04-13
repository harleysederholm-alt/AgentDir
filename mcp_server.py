"""
mcp_server.py — Local Model Context Protocol (MCP) Server
Avaa MCP-yhteensopivan rajapinnan AgentDirin ChromaDB:hen ja AST Sandboxiin.
Tämä mahdollistaa esim. Clauden ja Cursorin suoran RAG-haun AgentDiristä.
"""

from fastapi import APIRouter, HTTPException, Request
import json
import logging
import asyncio

logger = logging.getLogger("agentdir.mcp")
mcp_router = APIRouter(prefix="/mcp", tags=["MCP Server"])

@mcp_router.post("/v1/tools/call")
async def call_tool(request: Request):
    """
    Standardi MCP tool call endpoint.
    Mahdollistaa RAG-haut ja hiekkalaatikkokoodin suorituksen.
    """
    data = await request.json()
    tool_name = data.get("name")
    params = data.get("parameters", {})
    
    if tool_name == "rag_search":
        from server import get_server_config
        from rag_memory import RAGMemory
        query = params.get("query", "")
        n = params.get("n_results", 3)
        rag = RAGMemory(get_server_config())
        res = rag.query(query, n_results=n)
        return {"content": [{"type": "text", "text": res}], "isError": False}
        
    elif tool_name == "run_sandbox":
        from sandbox_executor import execute as sandbox_exec
        code = params.get("code", "")
        res = sandbox_exec(code)
        if res["success"]:
            return {"content": [{"type": "text", "text": res["output"]}], "isError": False}
        else:
            return {"content": [{"type": "text", "text": res["error"]}], "isError": True}
        
    raise HTTPException(status_code=404, detail="Tool not found")

@mcp_router.get("/v1/tools")
async def list_tools():
    """Palauttaa tuetut MCP-työkalut klienseille."""
    return {
        "tools": [
            {
                "name": "rag_search",
                "description": "Searches the AgentDir local ChromaDB memory for context.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "n_results": {"type": "integer"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "run_sandbox",
                "description": "Executes python code in the isolated AST Windows sandbox.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"}
                    },
                    "required": ["code"]
                }
            }
        ]
    }
