"""Unified vector tool that consolidates all vector/semantic search functionality."""

import asyncio
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, final, override

import httpx
from mcp.server import FastMCP
from mcp.server.fastmcp import Context as MCPContext

from hanzo_mcp.tools.common.base import BaseTool
from hanzo_mcp.tools.common.context import create_tool_context

logger = logging.getLogger(__name__)

# Try to import LanceDB and hanzo-memory dependencies
try:
    import lancedb
    from hanzo_memory.db.lancedb_client import get_lancedb_client
    from hanzo_memory.services.memory import get_memory_service
    from hanzo_memory.models.memory import Memory
    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False


class HanzoNodeClient:
    """Client for communicating with hanzo-node."""
    
    def __init__(self, base_url: str = "http://localhost:3690"):
        """Initialize hanzo-node client."""
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def is_available(self) -> bool:
        """Check if hanzo-node is running and available."""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False
            
    async def search_vectors(self, query: str, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Search vectors using hanzo-node."""
        try:
            payload = {
                "query": query,
                "limit": limit,
                **kwargs
            }
            response = await self.client.post(f"{self.base_url}/api/v1/search", json=payload)
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            logger.error(f"Error searching vectors via hanzo-node: {e}")
            return []
            
    async def index_content(self, content: str, metadata: Optional[Dict] = None) -> bool:
        """Index content using hanzo-node."""
        try:
            payload = {
                "content": content,
                "metadata": metadata or {}
            }
            response = await self.client.post(f"{self.base_url}/api/v1/index", json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error indexing content via hanzo-node: {e}")
            return False


@final
class UnifiedVectorTool(BaseTool):
    """Unified vector tool that consolidates all vector/semantic search functionality.
    
    This tool provides a single interface for vector operations that:
    1. Detects if hanzo-node is running on localhost:3690
    2. Uses hanzo-node for vector operations if available
    3. Falls back to embedded LanceDB if hanzo-node is not available
    4. Provides semantic search, indexing, and memory operations
    """
    
    def __init__(self, user_id: str = "default", project_id: str = "default"):
        """Initialize unified vector tool."""
        self.user_id = user_id
        self.project_id = project_id
        self.hanzo_node = HanzoNodeClient()
        
        # Initialize LanceDB fallback if available
        if LANCEDB_AVAILABLE:
            self.lancedb_client = get_lancedb_client()
            self.memory_service = get_memory_service()
        else:
            self.lancedb_client = None
            self.memory_service = None
            
    @property
    @override
    def name(self) -> str:
        """Get the tool name."""
        return "vector"
        
    @property
    @override
    def description(self) -> str:
        """Get the tool description."""
        return """Unified vector search and semantic operations.

This tool provides comprehensive vector/semantic search capabilities:
- Semantic search across indexed content
- Content indexing for future search
- Memory storage and retrieval
- Knowledge base operations

The tool automatically detects if hanzo-node is available and uses it for 
optimal performance, falling back to embedded LanceDB if needed.

Examples:
vector(action="search", query="error handling in Python", limit=5)
vector(action="index", content="Important project documentation", metadata={"type": "docs"})
vector(action="memory_create", content="User prefers TypeScript over JavaScript")
vector(action="memory_search", query="user preferences")
vector(action="status")  # Check backend status
"""

    async def _detect_backend(self) -> str:
        """Detect which backend to use."""
        if await self.hanzo_node.is_available():
            return "hanzo-node"
        elif LANCEDB_AVAILABLE:
            return "lancedb"
        else:
            return "none"
            
    async def _search_hanzo_node(self, query: str, limit: int, **kwargs) -> List[Dict[str, Any]]:
        """Search using hanzo-node."""
        return await self.hanzo_node.search_vectors(query, limit, **kwargs)
        
    async def _search_lancedb(self, query: str, limit: int, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search using embedded LanceDB."""
        if not self.memory_service:
            return []
            
        try:
            # Use hanzo-memory service for search
            results = self.memory_service.search_memories(
                user_id=self.user_id,
                query=query,
                project_id=project_id or self.project_id,
                limit=limit
            )
            
            # Convert to standard format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result.content,
                    "score": getattr(result, "similarity_score", 0.0),
                    "metadata": getattr(result, "metadata", {}),
                    "id": result.memory_id
                })
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching LanceDB: {e}")
            return []
            
    async def _index_hanzo_node(self, content: str, metadata: Optional[Dict] = None) -> bool:
        """Index content using hanzo-node."""
        return await self.hanzo_node.index_content(content, metadata)
        
    async def _index_lancedb(self, content: str, metadata: Optional[Dict] = None) -> bool:
        """Index content using embedded LanceDB."""
        if not self.memory_service:
            return False
            
        try:
            self.memory_service.create_memory(
                user_id=self.user_id,
                project_id=self.project_id,
                content=content,
                metadata=metadata or {}
            )
            return True
        except Exception as e:
            logger.error(f"Error indexing to LanceDB: {e}")
            return False

    @override
    async def call(
        self,
        ctx: MCPContext,
        action: str,
        query: Optional[str] = None,
        content: Optional[str] = None,
        limit: int = 10,
        project_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """Execute vector operations.
        
        Args:
            ctx: MCP context
            action: Action to perform (search, index, memory_create, memory_search, status)
            query: Search query (for search actions)
            content: Content to index or store (for index/create actions)
            limit: Maximum results to return
            project_id: Project ID (defaults to tool's project_id)
            metadata: Additional metadata
            **kwargs: Additional action-specific parameters
            
        Returns:
            Formatted results or status message
        """
        tool_ctx = create_tool_context(ctx)
        await tool_ctx.set_tool_info(self.name)
        
        # Detect backend
        backend = await self._detect_backend()
        await tool_ctx.info(f"Using backend: {backend}")
        
        if action == "status":
            return await self._handle_status(tool_ctx, backend)
        elif action == "search":
            return await self._handle_search(tool_ctx, backend, query, limit, project_id, **kwargs)
        elif action == "index":
            return await self._handle_index(tool_ctx, backend, content, metadata)
        elif action == "memory_create":
            return await self._handle_memory_create(tool_ctx, content, metadata)
        elif action == "memory_search":
            return await self._handle_memory_search(tool_ctx, query, limit, project_id)
        else:
            return f"Unknown action: {action}. Available actions: search, index, memory_create, memory_search, status"
            
    async def _handle_status(self, tool_ctx, backend: str) -> str:
        """Handle status check."""
        status_info = [f"Vector backend: {backend}"]
        
        if backend == "hanzo-node":
            try:
                node_available = await self.hanzo_node.is_available()
                status_info.append(f"Hanzo-node available: {node_available}")
                status_info.append(f"Hanzo-node URL: {self.hanzo_node.base_url}")
            except Exception as e:
                status_info.append(f"Hanzo-node error: {e}")
                
        if backend == "lancedb" or backend == "hanzo-node":
            status_info.append(f"LanceDB available: {LANCEDB_AVAILABLE}")
            if LANCEDB_AVAILABLE and self.lancedb_client:
                try:
                    # Check LanceDB status
                    db_path = Path(self.lancedb_client.db_path)
                    status_info.append(f"LanceDB path: {db_path}")
                    status_info.append(f"LanceDB exists: {db_path.exists()}")
                    if db_path.exists():
                        status_info.append(f"Table count: {len(self.lancedb_client.db.table_names())}")
                except Exception as e:
                    status_info.append(f"LanceDB error: {e}")
                    
        if backend == "none":
            status_info.append("No vector backend available. Install hanzo-memory or start hanzo-node.")
            
        return "\n".join(status_info)
        
    async def _handle_search(self, tool_ctx, backend: str, query: Optional[str], limit: int, project_id: Optional[str], **kwargs) -> str:
        """Handle search operations."""
        if not query:
            return "Error: Query is required for search action"
            
        await tool_ctx.info(f"Searching for: {query} (limit: {limit})")
        
        if backend == "hanzo-node":
            results = await self._search_hanzo_node(query, limit, **kwargs)
        elif backend == "lancedb":
            results = await self._search_lancedb(query, limit, project_id)
        else:
            return "Error: No vector backend available"
            
        if not results:
            return f"No results found for query: {query}"
            
        # Format results
        formatted = [f"Found {len(results)} results for '{query}':\n"]
        for i, result in enumerate(results, 1):
            content = result.get("content", "")
            score = result.get("score", 0.0)
            formatted.append(f"{i}. {content} (score: {score:.3f})")
            
        return "\n".join(formatted)
        
    async def _handle_index(self, tool_ctx, backend: str, content: Optional[str], metadata: Optional[Dict]) -> str:
        """Handle indexing operations."""
        if not content:
            return "Error: Content is required for index action"
            
        await tool_ctx.info(f"Indexing content: {content[:100]}...")
        
        if backend == "hanzo-node":
            success = await self._index_hanzo_node(content, metadata)
        elif backend == "lancedb":
            success = await self._index_lancedb(content, metadata)
        else:
            return "Error: No vector backend available"
            
        if success:
            return f"Successfully indexed content (backend: {backend})"
        else:
            return f"Failed to index content (backend: {backend})"
            
    async def _handle_memory_create(self, tool_ctx, content: Optional[str], metadata: Optional[Dict]) -> str:
        """Handle memory creation."""
        if not content:
            return "Error: Content is required for memory_create action"
            
        if not self.memory_service:
            return "Error: Memory service not available"
            
        try:
            memory = self.memory_service.create_memory(
                user_id=self.user_id,
                project_id=self.project_id,
                content=content,
                metadata=metadata or {}
            )
            return f"Created memory: {memory.memory_id}"
        except Exception as e:
            return f"Error creating memory: {e}"
            
    async def _handle_memory_search(self, tool_ctx, query: Optional[str], limit: int, project_id: Optional[str]) -> str:
        """Handle memory search."""
        if not query:
            return "Error: Query is required for memory_search action"
            
        if not self.memory_service:
            return "Error: Memory service not available"
            
        try:
            results = self.memory_service.search_memories(
                user_id=self.user_id,
                query=query,
                project_id=project_id or self.project_id,
                limit=limit
            )
            
            if not results:
                return f"No memories found for query: {query}"
                
            formatted = [f"Found {len(results)} memories for '{query}':\n"]
            for i, memory in enumerate(results, 1):
                score = getattr(memory, "similarity_score", 0.0)
                formatted.append(f"{i}. {memory.content} (score: {score:.3f})")
                
            return "\n".join(formatted)
        except Exception as e:
            return f"Error searching memories: {e}"

    @override
    def register(self, mcp_server: FastMCP) -> None:
        """Register this tool with the MCP server."""
        tool_self = self
        
        @mcp_server.tool(name=self.name, description=self.description)
        async def vector(
            ctx: MCPContext,
            action: str,
            query: Optional[str] = None,
            content: Optional[str] = None,
            limit: int = 10,
            project_id: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None,
        ) -> str:
            return await tool_self.call(
                ctx,
                action=action,
                query=query,
                content=content,
                limit=limit,
                project_id=project_id,
                metadata=metadata,
            )