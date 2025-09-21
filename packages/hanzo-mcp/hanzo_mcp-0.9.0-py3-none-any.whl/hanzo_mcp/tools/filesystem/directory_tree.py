"""Directory tree tool implementation.

This module provides the DirectoryTreeTool for viewing file and directory structures
with optional pagination and different display styles.
"""

from typing import Any, Dict, List, Union, Unpack, Optional, Literal, Annotated, TypedDict, final, override
from pathlib import Path
import fnmatch

from pydantic import Field
from mcp.server import FastMCP
from mcp.server.fastmcp import Context as MCPContext

from hanzo_mcp.tools.common.truncate import truncate_response
from hanzo_mcp.tools.filesystem.base import FilesystemBaseTool
from hanzo_mcp.tools.common.pagination import (
    CursorManager,
    paginate_list,
)

DirectoryPath = Annotated[
    str,
    Field(
        description="The path to the directory to view",
        title="Path",
    ),
]

Depth = Annotated[
    int,
    Field(
        default=3,
        description="The maximum depth to traverse (0 for unlimited)",
        title="Depth",
    ),
]

IncludeFiltered = Annotated[
    bool,
    Field(
        default=False,
        description="Include directories that are normally filtered",
        title="Include Filtered",
    ),
]

PageSize = Annotated[
    Optional[int],
    Field(
        default=None,
        description="Number of entries per page (enables pagination when set)",
        title="Page Size",
    ),
]

Page = Annotated[
    int,
    Field(
        default=1,
        description="Page number for pagination",
        title="Page",
    ),
]

Style = Annotated[
    Literal["compact", "detailed", "unix"],
    Field(
        default="compact",
        description="Display style: compact (default), detailed (with sizes), or unix (tree-like)",
        title="Style",
    ),
]


class DirectoryTreeToolParams(TypedDict, total=False):
    """Parameters for the DirectoryTreeTool.

    Attributes:
        path: The path to the directory to view
        depth: The maximum depth to traverse (0 for unlimited)
        include_filtered: Include directories that are normally filtered
        page_size: Number of entries per page (enables pagination when set)
        page: Page number for pagination
        style: Display style (compact, detailed, unix)
    """

    path: str
    depth: int
    include_filtered: bool
    page_size: Optional[int]
    page: int
    style: Literal["compact", "detailed", "unix"]


@final
class DirectoryTreeTool(FilesystemBaseTool):
    """Tool for viewing directory structure as a tree."""

    @property
    @override
    def name(self) -> str:
        """Get the tool name.

        Returns:
            Tool name
        """
        return "directory_tree"

    @property
    @override
    def description(self) -> str:
        """Get the tool description.

        Returns:
            Tool description
        """
        return """Get a recursive tree view of files and directories with customizable depth and filtering.

Returns a structured view of the directory tree with files and subdirectories.
Directories are marked with trailing slashes. The output is formatted as an
indented list for readability. By default, common development directories like
.git, node_modules, and venv are noted but not traversed unless explicitly
requested. Only works within allowed directories.

Supports multiple display styles:
- compact: Simple indented list (default)
- detailed: Includes file sizes and additional metadata
- unix: Traditional unix tree command style with ASCII art

Optional pagination is available by setting page_size parameter."""

    @override
    async def call(
        self,
        ctx: MCPContext,
        **params: Unpack[DirectoryTreeToolParams],
    ) -> Union[str, Dict[str, Any]]:
        """Execute the tool with the given parameters.

        Args:
            ctx: MCP context
            **params: Tool parameters

        Returns:
            Tool result
        """
        tool_ctx = self.create_tool_context(ctx)

        # Extract parameters
        path: str = params["path"]
        depth = params.get("depth", 3)  # Default depth is 3
        include_filtered = params.get("include_filtered", False)  # Default to False
        page_size = params.get("page_size")  # Optional pagination
        page = params.get("page", 1)
        style = params.get("style", "compact")

        # Expand path (handles ~, $HOME, etc.)
        path = self.expand_path(path)
        
        # For pagination, we need to use offset-based pagination
        offset = (page - 1) * page_size if page_size else None

        # Validate path parameter
        path_validation = self.validate_path(path)
        if path_validation.is_error:
            await tool_ctx.error(path_validation.error_message)
            return f"Error: {path_validation.error_message}"

        pagination_info = f" (page {page}, size {page_size})" if page_size else ""
        await tool_ctx.info(f"Getting directory tree: {path} (depth: {depth}, include_filtered: {include_filtered}, style: {style}){pagination_info}")

        # Check if path is allowed
        allowed, error_msg = await self.check_path_allowed(path, tool_ctx)
        if not allowed:
            return error_msg

        try:
            dir_path = Path(path)

            # Check if path exists
            exists, error_msg = await self.check_path_exists(path, tool_ctx)
            if not exists:
                return error_msg

            # Check if path is a directory
            is_dir, error_msg = await self.check_is_directory(path, tool_ctx)
            if not is_dir:
                return error_msg

            # Define filtered directories
            FILTERED_DIRECTORIES = {
                ".git",
                "node_modules",
                ".venv",
                "venv",
                "__pycache__",
                ".pytest_cache",
                ".idea",
                ".vs",
                ".vscode",
                "dist",
                "build",
                "target",
                ".ruff_cache",
                ".llm-context",
            }

            # Log filtering settings
            await tool_ctx.info(f"Directory tree filtering: include_filtered={include_filtered}")

            # Check if a directory should be filtered
            def should_filter(current_path: Path) -> bool:
                # Don't filter if it's the explicitly requested path
                if str(current_path.absolute()) == str(dir_path.absolute()):
                    # Don't filter explicitly requested paths
                    return False

                # Filter based on directory name if filtering is enabled
                return current_path.name in FILTERED_DIRECTORIES and not include_filtered

            # Track stats for summary
            stats = {
                "directories": 0,
                "files": 0,
                "skipped_depth": 0,
                "skipped_filtered": 0,
            }

            # If pagination is enabled, collect entries in a flat list
            if page_size:
                all_entries: List[Dict[str, Any]] = []
                
                async def collect_entries(current_path: Path, current_depth: int = 0, parent_path: str = "") -> None:
                    """Collect entries in a flat list for pagination."""
                    if not self.is_path_allowed(str(current_path)):
                        return

                    try:
                        # Sort entries: directories first, then files alphabetically
                        entries = sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

                        for entry in entries:
                            if not self.is_path_allowed(str(entry)):
                                continue

                            # Calculate relative path for display
                            relative_path = f"{parent_path}/{entry.name}" if parent_path else entry.name

                            if entry.is_dir():
                                stats["directories"] += 1
                                entry_data: Dict[str, Any] = {
                                    "path": relative_path,
                                    "name": entry.name,
                                    "type": "directory",
                                    "depth": current_depth,
                                }

                                # Add size info for detailed style
                                if style == "detailed":
                                    try:
                                        entry_data["size"] = sum(f.stat().st_size for f in entry.rglob('*') if f.is_file())
                                    except Exception:
                                        entry_data["size"] = 0

                                # Check if we should filter this directory
                                if should_filter(entry):
                                    entry_data["skipped"] = "filtered-directory"
                                    stats["skipped_filtered"] += 1
                                    all_entries.append(entry_data)
                                    continue

                                # Check depth limit
                                if depth > 0 and current_depth >= depth:
                                    entry_data["skipped"] = "depth-limit"
                                    stats["skipped_depth"] += 1
                                    all_entries.append(entry_data)
                                    continue

                                # Add directory entry
                                all_entries.append(entry_data)

                                # Process children recursively
                                await collect_entries(entry, current_depth + 1, relative_path)
                            else:
                                # Add file entry
                                if depth <= 0 or current_depth < depth:
                                    stats["files"] += 1
                                    file_data = {
                                        "path": relative_path,
                                        "name": entry.name,
                                        "type": "file",
                                        "depth": current_depth,
                                    }
                                    
                                    # Add size info for detailed style
                                    if style == "detailed":
                                        try:
                                            file_data["size"] = entry.stat().st_size
                                        except Exception:
                                            file_data["size"] = 0
                                    
                                    all_entries.append(file_data)

                    except Exception as e:
                        await tool_ctx.warning(f"Error processing {current_path}: {str(e)}")
                
                # Collect all entries
                await tool_ctx.info("Collecting directory entries for pagination...")
                await collect_entries(dir_path)
                
                # Apply pagination using offset
                start_idx = offset if offset else 0
                end_idx = start_idx + page_size
                paginated_entries = all_entries[start_idx:end_idx]
                
                # Format entries based on style
                formatted_entries = self._format_entries(paginated_entries, style)
                
                # Build paginated response
                response = {
                    "entries": formatted_entries,
                    "total_entries": len(all_entries),
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (len(all_entries) + page_size - 1) // page_size,
                    "has_next": end_idx < len(all_entries),
                    "stats": {
                        "directories": stats["directories"],
                        "files": stats["files"],
                        "skipped_depth": stats["skipped_depth"],
                        "skipped_filtered": stats["skipped_filtered"],
                    }
                }
                
                return response
            
            # Non-paginated: Build the tree recursively
            async def build_tree(current_path: Path, current_depth: int = 0) -> list[dict[str, Any]]:
                result: list[dict[str, Any]] = []

                # Skip processing if path isn't allowed
                if not self.is_path_allowed(str(current_path)):
                    return result

                try:
                    # Sort entries: directories first, then files alphabetically
                    entries = sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

                    for entry in entries:
                        # Skip entries that aren't allowed
                        if not self.is_path_allowed(str(entry)):
                            continue

                        if entry.is_dir():
                            stats["directories"] += 1
                            entry_data: dict[str, Any] = {
                                "name": entry.name,
                                "type": "directory",
                            }
                            
                            # Add size info for detailed style
                            if style == "detailed":
                                try:
                                    entry_data["size"] = sum(f.stat().st_size for f in entry.rglob('*') if f.is_file())
                                except Exception:
                                    entry_data["size"] = 0

                            # Check if we should filter this directory
                            if should_filter(entry):
                                entry_data["skipped"] = "filtered-directory"
                                stats["skipped_filtered"] += 1
                                result.append(entry_data)
                                continue

                            # Check depth limit (if enabled)
                            if depth > 0 and current_depth >= depth:
                                entry_data["skipped"] = "depth-limit"
                                stats["skipped_depth"] += 1
                                result.append(entry_data)
                                continue

                            # Process children recursively with depth increment
                            entry_data["children"] = await build_tree(entry, current_depth + 1)
                            result.append(entry_data)
                        else:
                            # Files should be at the same level check as directories
                            if depth <= 0 or current_depth < depth:
                                stats["files"] += 1
                                file_data = {"name": entry.name, "type": "file"}
                                
                                # Add size info for detailed style
                                if style == "detailed":
                                    try:
                                        file_data["size"] = entry.stat().st_size
                                    except Exception:
                                        file_data["size"] = 0
                                
                                result.append(file_data)

                except Exception as e:
                    await tool_ctx.warning(f"Error processing {current_path}: {str(e)}")

                return result

            # Format the tree based on style
            def format_tree(tree_data: list[dict[str, Any]], level: int = 0, prefix: str = "", is_last: bool = True) -> list[str]:
                lines = []

                for i, item in enumerate(tree_data):
                    is_last_item = i == len(tree_data) - 1
                    
                    if style == "unix":
                        # Unix tree style with ASCII art
                        if level == 0:
                            current_prefix = ""
                            next_prefix = ""
                        else:
                            if is_last_item:
                                current_prefix = prefix + "└── "
                                next_prefix = prefix + "    "
                            else:
                                current_prefix = prefix + "├── "
                                next_prefix = prefix + "│   "
                    else:
                        # Compact or detailed style with simple indentation
                        current_prefix = "  " * level
                        next_prefix = "  " * (level + 1)

                    # Format based on type
                    if item["type"] == "directory":
                        if "skipped" in item:
                            line = f"{current_prefix}{item['name']}/ [skipped - {item['skipped']}]"
                        else:
                            line = f"{current_prefix}{item['name']}/"
                            if style == "detailed" and "size" in item:
                                line += f" ({self._format_size(item['size'])})"
                        lines.append(line)
                        
                        # Add children with increased indentation if present
                        if "children" in item and "skipped" not in item:
                            lines.extend(format_tree(item["children"], level + 1, next_prefix, is_last_item))
                    else:
                        # File
                        line = f"{current_prefix}{item['name']}"
                        if style == "detailed" and "size" in item:
                            line += f" ({self._format_size(item['size'])})"
                        lines.append(line)

                return lines

            # Build tree starting from the requested directory
            tree_data = await build_tree(dir_path)

            # Format based on style
            if style == "unix":
                # Start with the root directory name
                formatted_lines = [str(dir_path)]
                formatted_lines.extend(format_tree(tree_data))
            else:
                formatted_lines = format_tree(tree_data)
            
            formatted_output = "\n".join(formatted_lines)

            # Add stats summary
            summary = (
                f"\nDirectory Stats: {stats['directories']} directories, {stats['files']} files "
                f"({stats['skipped_depth']} skipped due to depth limit, "
                f"{stats['skipped_filtered']} filtered directories skipped)"
            )

            await tool_ctx.info(
                f"Generated directory tree for {path} (depth: {depth}, include_filtered: {include_filtered}, style: {style})"
            )

            # Truncate response to stay within token limits
            full_response = formatted_output + summary
            return truncate_response(
                full_response,
                max_tokens=25000,
                truncation_message="\n\n[Response truncated due to token limit. Please use pagination (page_size parameter) or a smaller depth.]",
            )
        except Exception as e:
            await tool_ctx.error(f"Error generating directory tree: {str(e)}")
            if page_size:
                return {"error": f"Error generating directory tree: {str(e)}"}
            return f"Error generating directory tree: {str(e)}"
    
    def _format_entries(self, entries: List[Dict[str, Any]], style: str) -> List[str]:
        """Format entries for paginated output."""
        formatted = []
        for entry in entries:
            indent = "  " * entry["depth"]
            name = entry["name"]
            
            if entry["type"] == "directory":
                if "skipped" in entry:
                    line = f"{indent}{name}/ [skipped - {entry['skipped']}]"
                else:
                    line = f"{indent}{name}/"
                    if style == "detailed" and "size" in entry:
                        line += f" ({self._format_size(entry['size'])})"
            else:
                line = f"{indent}{name}"
                if style == "detailed" and "size" in entry:
                    line += f" ({self._format_size(entry['size'])})"
            
            formatted.append(line)
        return formatted
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}PB"

    @override
    def register(self, mcp_server: FastMCP) -> None:
        """Register this directory tree tool with the MCP server.

        Creates a wrapper function with explicitly defined parameters that match
        the tool's parameter schema and registers it with the MCP server.

        Args:
            mcp_server: The FastMCP server instance
        """
        tool_self = self  # Create a reference to self for use in the closure

        @mcp_server.tool(name=self.name, description=self.description)
        async def directory_tree(
            ctx: MCPContext,
            path: DirectoryPath,
            depth: Depth = 3,
            include_filtered: IncludeFiltered = False,
            page_size: PageSize = None,
            page: Page = 1,
            style: Style = "compact",
        ) -> Union[str, Dict[str, Any]]:
            return await tool_self.call(
                ctx, 
                path=path, 
                depth=depth, 
                include_filtered=include_filtered,
                page_size=page_size,
                page=page,
                style=style
            )
