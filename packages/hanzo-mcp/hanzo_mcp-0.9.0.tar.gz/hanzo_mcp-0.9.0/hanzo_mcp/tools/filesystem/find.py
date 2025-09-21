"""Unified find tool implementation.

This module provides the FindTool for finding files by name or content using
multiple search backends in order of preference: rg > ag > ack > grep.
"""

import os
import re
import json
import shutil
import asyncio
import fnmatch
from typing import (
    List,
    Unpack,
    Optional,
    Annotated,
    TypedDict,
    final,
    override,
    Literal,
)
from pathlib import Path

from pydantic import Field
from mcp.server.fastmcp import Context as MCPContext

from hanzo_mcp.tools.filesystem.base import FilesystemBaseTool

try:
    import ffind
    FFIND_AVAILABLE = True
except ImportError:
    FFIND_AVAILABLE = False

# Parameter types
Pattern = Annotated[
    str,
    Field(
        description="Pattern to search for (file name pattern or content regex/literal)",
        min_length=1,
    ),
]

SearchPath = Annotated[
    str,
    Field(
        description="Path to search in",
        default=".",
    ),
]

Mode = Annotated[
    Literal["name", "content", "both"],
    Field(
        description="Search mode: 'name' for file names, 'content' for file contents, 'both' for both",
        default="name",
    ),
]

Include = Annotated[
    Optional[str],
    Field(
        description='File pattern to include (e.g. "*.js", "*.{ts,tsx}")',
        default=None,
    ),
]

Exclude = Annotated[
    Optional[str],
    Field(
        description="File pattern to exclude",
        default=None,
    ),
]

CaseSensitive = Annotated[
    bool,
    Field(
        description="Case sensitive search",
        default=False,
    ),
]

Recursive = Annotated[
    bool,
    Field(
        description="Search recursively in subdirectories",
        default=True,
    ),
]

MaxResults = Annotated[
    Optional[int],
    Field(
        description="Maximum number of results to return",
        default=None,
    ),
]


class FindParams(TypedDict, total=False):
    """Parameters for find tool."""

    pattern: str
    path: str
    mode: Literal["name", "content", "both"]
    include: Optional[str]
    exclude: Optional[str]
    case_sensitive: bool
    recursive: bool
    max_results: Optional[int]


@final
class FindTool(FilesystemBaseTool):
    """Unified find tool for searching by file name or content."""

    def __init__(self, permission_manager):
        """Initialize the find tool."""
        super().__init__(permission_manager)
        self._backend_order = ["rg", "ag", "ack", "grep"]
        self._available_backends = None

    @property
    @override
    def name(self) -> str:
        """Get the tool name."""
        return "find"

    @property
    @override
    def description(self) -> str:
        """Get the tool description."""
        backends = self._get_available_backends()
        backend_str = ", ".join(backends) if backends else "fallback search"

        return f"""Find files by name, content, or both. Available backends: {backend_str}.

Examples:
# Find by file name (default mode)
find "*.py" 
find "test_*" ./src
find "README.*" --case-sensitive

# Find by content 
find "TODO" --mode content
find "error.*fatal" ./src --mode content

# Find both name and content
find "config" --mode both --include "*.json"

Supports wildcards for names, regex for content."""

    def _get_available_backends(self) -> List[str]:
        """Get list of available search backends."""
        if self._available_backends is None:
            self._available_backends = []
            for backend in self._backend_order:
                if shutil.which(backend):
                    self._available_backends.append(backend)
        return self._available_backends

    @override
    async def call(
        self,
        ctx: MCPContext,
        **params: Unpack[FindParams],
    ) -> str:
        """Execute find operation."""
        tool_ctx = self.create_tool_context(ctx)

        # Extract parameters
        pattern = params.get("pattern")
        if not pattern:
            return "Error: pattern is required"

        path = params.get("path", ".")
        mode = params.get("mode", "name")
        include = params.get("include")
        exclude = params.get("exclude")
        case_sensitive = params.get("case_sensitive", False)
        recursive = params.get("recursive", True)
        max_results = params.get("max_results")

        # Expand path (handles ~, $HOME, etc.)
        path = self.expand_path(path)

        # Validate path
        path_validation = self.validate_path(path)
        if path_validation.is_error:
            await tool_ctx.error(path_validation.error_message)
            return f"Error: {path_validation.error_message}"

        # Check permissions
        allowed, error_msg = await self.check_path_allowed(path, tool_ctx)
        if not allowed:
            return error_msg

        # Check existence
        exists, error_msg = await self.check_path_exists(path, tool_ctx)
        if not exists:
            return error_msg

        await tool_ctx.info(f"Searching for '{pattern}' in {path} (mode: {mode})")

        # Route to appropriate search method
        if mode == "name":
            return await self._find_by_name(
                pattern, path, include, exclude, case_sensitive, recursive, max_results, tool_ctx
            )
        elif mode == "content":
            return await self._find_by_content(
                pattern, path, include, exclude, case_sensitive, max_results, tool_ctx
            )
        elif mode == "both":
            return await self._find_both(
                pattern, path, include, exclude, case_sensitive, recursive, max_results, tool_ctx
            )
        else:
            return f"Error: Invalid mode '{mode}'. Use 'name', 'content', or 'both'."

    async def _find_by_name(
        self, pattern, path, include, exclude, case_sensitive, recursive, max_results, tool_ctx
    ) -> str:
        """Find files by name pattern."""
        search_path = path or os.getcwd()
        
        # If ffind is not available, fall back to basic implementation
        if not FFIND_AVAILABLE:
            return await self._find_files_fallback(
                pattern, search_path, recursive, not case_sensitive, False, False, True, max_results or 100
            )

        try:
            # Use ffind for efficient searching
            results = []
            count = 0

            # Configure ffind options
            options = {
                "pattern": pattern,
                "path": search_path,
                "recursive": recursive,
                "ignore_case": not case_sensitive,
                "hidden": False,
            }

            # Search with ffind
            for filepath in ffind.find(**options):
                # Check if it matches our include/exclude criteria
                filename = os.path.basename(filepath)
                if not self._match_file_pattern(filename, include, exclude):
                    continue

                # Make path relative for cleaner output
                try:
                    rel_path = os.path.relpath(filepath, search_path)
                except ValueError:
                    rel_path = filepath

                results.append(rel_path)
                count += 1

                if max_results and count >= max_results:
                    break

            if not results:
                return f"No files found matching '{pattern}'"

            # Format output
            output = [f"Found {len(results)} file(s) matching '{pattern}':"]
            output.append("")

            for filepath in sorted(results):
                output.append(filepath)

            if max_results and count >= max_results:
                output.append(f"\n... (showing first {max_results} results)")

            return "\n".join(output)

        except Exception as e:
            await tool_ctx.error(f"Error during name search: {str(e)}")
            # Fall back to basic implementation
            return await self._find_files_fallback(
                pattern, search_path, recursive, not case_sensitive, False, False, True, max_results or 100
            )

    async def _find_by_content(
        self, pattern, path, include, exclude, case_sensitive, max_results, tool_ctx
    ) -> str:
        """Find files by content pattern."""
        # Select backend for content search
        available = self._get_available_backends()
        selected_backend = available[0] if available else "grep"

        await tool_ctx.info(f"Using {selected_backend} for content search")

        # Execute content search
        if selected_backend == "rg":
            return await self._run_ripgrep_content(
                pattern, path, include, exclude, case_sensitive, max_results, tool_ctx
            )
        elif selected_backend == "ag":
            return await self._run_silver_searcher_content(
                pattern, path, include, exclude, case_sensitive, max_results, tool_ctx
            )
        elif selected_backend == "ack":
            return await self._run_ack_content(
                pattern, path, include, exclude, case_sensitive, max_results, tool_ctx
            )
        else:
            return await self._run_fallback_grep_content(
                pattern, path, include, exclude, case_sensitive, max_results, tool_ctx
            )

    async def _find_both(
        self, pattern, path, include, exclude, case_sensitive, recursive, max_results, tool_ctx
    ) -> str:
        """Find files by both name and content."""
        # Run both searches
        name_results = await self._find_by_name(
            pattern, path, include, exclude, case_sensitive, recursive, max_results, tool_ctx
        )
        content_results = await self._find_by_content(
            pattern, path, include, exclude, case_sensitive, max_results, tool_ctx
        )

        # Combine results
        output = ["=== NAME MATCHES ==="]
        output.append(name_results)
        output.append("")
        output.append("=== CONTENT MATCHES ===")
        output.append(content_results)

        return "\n".join(output)

    async def _run_ripgrep_content(
        self, pattern, path, include, exclude, case_sensitive, max_results, tool_ctx
    ) -> str:
        """Run ripgrep backend for content search."""
        cmd = ["rg", "--json"]

        if not case_sensitive:
            cmd.append("-i")
        if include:
            cmd.extend(["-g", include])
        if exclude:
            cmd.extend(["-g", f"!{exclude}"])
        if max_results:
            cmd.extend(["-m", str(max_results)])

        cmd.extend([pattern, path])

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode not in [0, 1]:  # 1 = no matches
                await tool_ctx.error(f"ripgrep failed: {stderr.decode()}")
                return f"Error: {stderr.decode()}"

            return self._parse_ripgrep_output(stdout.decode())

        except Exception as e:
            await tool_ctx.error(f"Error running ripgrep: {str(e)}")
            return f"Error running ripgrep: {str(e)}"

    async def _run_silver_searcher_content(
        self, pattern, path, include, exclude, case_sensitive, max_results, tool_ctx
    ) -> str:
        """Run silver searcher (ag) backend for content search."""
        cmd = ["ag", "--nocolor", "--nogroup"]

        if not case_sensitive:
            cmd.append("-i")
        if include:
            cmd.extend(["-G", include])
        if exclude:
            cmd.extend(["--ignore", exclude])
        if max_results:
            cmd.extend(["-m", str(max_results)])

        cmd.extend([pattern, path])

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode not in [0, 1]:
                await tool_ctx.error(f"ag failed: {stderr.decode()}")
                return f"Error: {stderr.decode()}"

            output = stdout.decode()
            if not output.strip():
                return "No matches found."

            lines = output.strip().split("\n")
            return f"Found {len(lines)} matches:\n\n" + output

        except Exception as e:
            await tool_ctx.error(f"Error running ag: {str(e)}")
            return f"Error running ag: {str(e)}"

    async def _run_ack_content(
        self, pattern, path, include, exclude, case_sensitive, max_results, tool_ctx
    ) -> str:
        """Run ack backend for content search."""
        cmd = ["ack", "--nocolor", "--nogroup"]

        if not case_sensitive:
            cmd.append("-i")
        if include:
            # ack uses different syntax for file patterns
            cmd.extend([
                "--type-add",
                f"custom:ext:{include.replace('*.', '')}",
                "--type=custom",
            ])
        if max_results:
            cmd.extend(["-m", str(max_results)])

        cmd.extend([pattern, path])

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode not in [0, 1]:
                await tool_ctx.error(f"ack failed: {stderr.decode()}")
                return f"Error: {stderr.decode()}"

            output = stdout.decode()
            if not output.strip():
                return "No matches found."

            lines = output.strip().split("\n")
            return f"Found {len(lines)} matches:\n\n" + output

        except Exception as e:
            await tool_ctx.error(f"Error running ack: {str(e)}")
            return f"Error running ack: {str(e)}"

    async def _run_fallback_grep_content(
        self, pattern, path, include, exclude, case_sensitive, max_results, tool_ctx
    ) -> str:
        """Fallback Python implementation for content search."""
        await tool_ctx.info("Using fallback Python grep implementation")

        try:
            input_path = Path(path)
            matching_files = []

            # Get files to search
            if input_path.is_file():
                if self._match_file_pattern(input_path.name, include, exclude):
                    matching_files.append(input_path)
            else:
                for entry in input_path.rglob("*"):
                    if entry.is_file() and self.is_path_allowed(str(entry)):
                        if self._match_file_pattern(entry.name, include, exclude):
                            matching_files.append(entry)

            if not matching_files:
                return "No matching files found."

            # Compile pattern
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                regex = re.compile(pattern, flags)
            except re.error as e:
                return f"Error: Invalid regex pattern: {e}"

            # Search files
            results = []
            total_matches = 0

            for file_path in matching_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    for i, line in enumerate(lines, 1):
                        if regex.search(line):
                            results.append(f"{file_path}:{i}:{line.rstrip()}")
                            total_matches += 1
                            
                            if max_results and total_matches >= max_results:
                                break

                except UnicodeDecodeError:
                    pass  # Skip binary files
                except Exception as e:
                    await tool_ctx.warning(f"Error reading {file_path}: {str(e)}")

                if max_results and total_matches >= max_results:
                    break

            if not results:
                return "No matches found."

            return f"Found {total_matches} matches:\n\n" + "\n".join(results)

        except Exception as e:
            await tool_ctx.error(f"Error in fallback grep: {str(e)}")
            return f"Error in fallback grep: {str(e)}"

    async def _find_files_fallback(
        self,
        pattern: str,
        search_path: str,
        recursive: bool,
        ignore_case: bool,
        hidden: bool,
        dirs_only: bool,
        files_only: bool,
        max_results: int,
    ) -> str:
        """Fallback implementation for file name search when ffind is not available."""
        results = []
        count = 0

        # Convert pattern for case-insensitive matching
        if ignore_case:
            pattern = pattern.lower()

        try:
            if recursive:
                # Walk directory tree
                for root, dirs, files in os.walk(search_path):
                    # Skip hidden directories if not requested
                    if not hidden:
                        dirs[:] = [d for d in dirs if not d.startswith(".")]

                    # Check directories
                    if not files_only:
                        for dirname in dirs:
                            if self._match_pattern(dirname, pattern, ignore_case):
                                filepath = os.path.join(root, dirname)
                                rel_path = os.path.relpath(filepath, search_path)
                                results.append(rel_path + "/")
                                count += 1
                                if count >= max_results:
                                    break

                    # Check files
                    if not dirs_only:
                        for filename in files:
                            if not hidden and filename.startswith("."):
                                continue

                            if self._match_pattern(filename, pattern, ignore_case):
                                filepath = os.path.join(root, filename)
                                rel_path = os.path.relpath(filepath, search_path)
                                results.append(rel_path)
                                count += 1
                                if count >= max_results:
                                    break

                    if count >= max_results:
                        break
            else:
                # Only search in the specified directory
                for entry in os.listdir(search_path):
                    if not hidden and entry.startswith("."):
                        continue

                    filepath = os.path.join(search_path, entry)
                    is_dir = os.path.isdir(filepath)

                    if dirs_only and not is_dir:
                        continue
                    if files_only and is_dir:
                        continue

                    if self._match_pattern(entry, pattern, ignore_case):
                        results.append(entry + "/" if is_dir else entry)
                        count += 1
                        if count >= max_results:
                            break

            if not results:
                return f"No files found matching '{pattern}' (using fallback search)"

            # Format output
            output = [f"Found {len(results)} file(s) matching '{pattern}' (using fallback search):"]
            output.append("")

            for filepath in sorted(results):
                output.append(filepath)

            if count >= max_results:
                output.append(f"\n... (showing first {max_results} results)")

            if not FFIND_AVAILABLE:
                output.append("\nNote: Install 'ffind' for faster searching: pip install ffind")

            return "\n".join(output)

        except Exception as e:
            return f"Error searching for files: {str(e)}"

    def _match_pattern(self, filename: str, pattern: str, ignore_case: bool) -> bool:
        """Check if filename matches pattern."""
        if ignore_case:
            return fnmatch.fnmatch(filename.lower(), pattern)
        else:
            return fnmatch.fnmatch(filename, pattern)

    def _match_file_pattern(self, filename: str, include: Optional[str], exclude: Optional[str]) -> bool:
        """Check if filename matches include/exclude patterns."""
        if include and not fnmatch.fnmatch(filename, include):
            return False
        if exclude and fnmatch.fnmatch(filename, exclude):
            return False
        return True

    def _parse_ripgrep_output(self, output: str) -> str:
        """Parse ripgrep JSON output."""
        if not output.strip():
            return "No matches found."

        results = []
        total_matches = 0

        for line in output.splitlines():
            if not line.strip():
                continue

            try:
                data = json.loads(line)

                if data.get("type") == "match":
                    match_data = data.get("data", {})
                    path = match_data.get("path", {}).get("text", "")
                    line_number = match_data.get("line_number", 0)
                    line_text = match_data.get("lines", {}).get("text", "").rstrip()

                    results.append(f"{path}:{line_number}:{line_text}")
                    total_matches += 1

                elif data.get("type") == "context":
                    context_data = data.get("data", {})
                    path = context_data.get("path", {}).get("text", "")
                    line_number = context_data.get("line_number", 0)
                    line_text = context_data.get("lines", {}).get("text", "").rstrip()

                    results.append(f"{path}:{line_number}-{line_text}")

            except json.JSONDecodeError:
                pass

        if not results:
            return "No matches found."

        return f"Found {total_matches} matches:\n\n" + "\n".join(results)

    def register(self, mcp_server) -> None:
        """Register this tool with the MCP server."""
        pass