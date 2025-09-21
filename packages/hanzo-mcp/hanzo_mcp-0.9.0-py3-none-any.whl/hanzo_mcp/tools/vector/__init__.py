"""Vector database tools for Hanzo AI.

This package provides tools for working with local vector databases for semantic search,
document indexing, and retrieval-augmented generation (RAG) workflows.

Supported backends:
- LanceDB (primary) - High-performance embedded vector database
- Hanzo-node (optional) - Distributed vector processing node
- Infinity database (legacy) - High-performance local vector database
"""

from mcp.server import FastMCP

from hanzo_mcp.tools.common.base import BaseTool, ToolRegistry
from hanzo_mcp.tools.common.permissions import PermissionManager

# Try to import unified vector tools first
try:
    from .unified_vector import UnifiedVectorTool
    from .node_tool import NodeTool
    
    UNIFIED_TOOLS_AVAILABLE = True
except ImportError:
    UNIFIED_TOOLS_AVAILABLE = False

# Try to import legacy vector dependencies
try:
    from .index_tool import IndexTool
    from .vector_index import VectorIndexTool
    from .vector_search import VectorSearchTool
    from .infinity_store import InfinityVectorStore
    from .project_manager import ProjectVectorManager

    LEGACY_VECTOR_AVAILABLE = True
except ImportError:
    LEGACY_VECTOR_AVAILABLE = False


def register_vector_tools(
    mcp_server: FastMCP,
    permission_manager: PermissionManager | None = None,
    vector_config: dict | None = None,
    enabled_tools: dict[str, bool] | None = None,
    search_paths: list[str] | None = None,
    project_manager: "ProjectVectorManager | None" = None,
    user_id: str = "default",
    project_id: str = "default",
    use_unified: bool = True,
) -> list[BaseTool]:
    """Register vector database tools with the MCP server.

    Args:
        mcp_server: The FastMCP server instance
        permission_manager: Permission manager for access control (optional for unified tools)
        vector_config: Vector store configuration
        enabled_tools: Dictionary of individual tool enable states
        search_paths: Paths to search for projects (default: None, uses allowed paths)
        project_manager: Optional existing project manager to reuse
        user_id: User ID for unified tools
        project_id: Project ID for unified tools
        use_unified: Whether to use unified tools (default: True)

    Returns:
        List of registered tools
    """
    tools = []
    
    # Prefer unified tools if available and enabled
    if use_unified and UNIFIED_TOOLS_AVAILABLE:
        tool_enabled = enabled_tools or {}
        
        # Register unified vector tool (consolidates vector_search, vector_index, memory ops)
        if tool_enabled.get("vector", True):
            unified_vector = UnifiedVectorTool(user_id=user_id, project_id=project_id)
            ToolRegistry.register_tool(mcp_server, unified_vector)
            tools.append(unified_vector)
            
        # Register node management tool
        if tool_enabled.get("node", True):
            node_tool = NodeTool()
            ToolRegistry.register_tool(mcp_server, node_tool)
            tools.append(node_tool)
            
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Registered {len(tools)} unified vector tools")
        
    # Fall back to legacy tools if unified not available or disabled
    elif not use_unified and LEGACY_VECTOR_AVAILABLE:
        if not vector_config or not vector_config.get("enabled", False):
            return []

        if not permission_manager:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Permission manager required for legacy vector tools")
            return []

        # Check individual tool enablement
        tool_enabled = enabled_tools or {}

        # Use provided project manager or create new one
        if project_manager is None:
            # Initialize project-aware vector manager
            store_config = vector_config.copy()
            project_manager = ProjectVectorManager(
                global_db_path=store_config.get("data_path"),
                embedding_model=store_config.get("embedding_model", "text-embedding-3-small"),
                dimension=store_config.get("dimension", 1536),
            )

            # Auto-detect projects from search paths for new manager
            if search_paths:
                detected_projects = project_manager.detect_projects(search_paths)
                import logging

                logger = logging.getLogger(__name__)
                logger.info(f"Detected {len(detected_projects)} projects with LLM.md files")

        # Register individual tools if enabled
        if tool_enabled.get("index", True):
            tools.append(IndexTool(permission_manager))

        if tool_enabled.get("vector_index", True):
            tools.append(VectorIndexTool(permission_manager, project_manager))

        if tool_enabled.get("vector_search", True):
            tools.append(VectorSearchTool(permission_manager, project_manager))

        # Register with MCP server
        ToolRegistry.register_tools(mcp_server, tools)
        
    else:
        import logging
        logger = logging.getLogger(__name__)
        if not UNIFIED_TOOLS_AVAILABLE and not LEGACY_VECTOR_AVAILABLE:
            logger.warning("No vector tools available. Install hanzo-memory package or infinity-embedded.")
        elif not use_unified:
            logger.info("Unified vector tools disabled, legacy tools not available")

    return tools


__all__ = [
    "register_vector_tools",
    "UNIFIED_TOOLS_AVAILABLE",
    "LEGACY_VECTOR_AVAILABLE",
]

if UNIFIED_TOOLS_AVAILABLE:
    __all__.extend(
        [
            "UnifiedVectorTool",
            "NodeTool",
        ]
    )

if LEGACY_VECTOR_AVAILABLE:
    __all__.extend(
        [
            "InfinityVectorStore",
            "ProjectVectorManager",
            "IndexTool",
            "VectorIndexTool",
            "VectorSearchTool",
        ]
    )
