"""Unified search tool implementation.

This module provides the unified search tool that combines multiple search strategies:
- Pattern search (regex/text) using ripgrep or fallback
- AST-aware code search with structural context
- Semantic similarity search using vector embeddings
- Git history search through commits and content
- Symbol search for function/class definitions

The tool can run single queries or batch multiple queries in parallel for comprehensive
code analysis and refactoring tasks.
"""

import re
import json
import shlex
import shutil
import asyncio
import fnmatch
from enum import Enum
from typing import (
    Dict,
    List,
    Tuple,
    Union,
    Unpack,
    Optional,
    Annotated,
    TypedDict,
    final,
    override,
    Literal,
)
from pathlib import Path
from dataclasses import dataclass

from pydantic import Field
from mcp.server import FastMCP
from mcp.server.fastmcp import Context as MCPContext

from hanzo_mcp.tools.common.context import ToolContext
from hanzo_mcp.tools.common.truncate import truncate_response
from hanzo_mcp.tools.filesystem.base import FilesystemBaseTool

# For optional dependencies
try:
    from hanzo_mcp.tools.vector.vector_search import VectorSearchTool
    from hanzo_mcp.tools.vector.project_manager import ProjectVectorManager
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VectorSearchTool = None
    ProjectVectorManager = None
    VECTOR_SEARCH_AVAILABLE = False

try:
    from hanzo_mcp.tools.filesystem.git_search import GitSearchTool
    GIT_SEARCH_AVAILABLE = True
except ImportError:
    GitSearchTool = None
    GIT_SEARCH_AVAILABLE = False

try:
    from hanzo_mcp.tools.filesystem.ast_tool import ASTTool
    AST_SEARCH_AVAILABLE = True
except ImportError:
    ASTTool = None
    AST_SEARCH_AVAILABLE = False


class SearchStrategy(Enum):
    """Search strategies available."""
    PATTERN = "pattern"
    AST = "ast"
    SEMANTIC = "semantic"
    GIT = "git"
    ALL = "all"


class SearchType(Enum):
    """Types of searches that can be performed."""
    GREP = "grep"
    GREP_AST = "grep_ast"
    VECTOR = "vector"
    GIT = "git"
    SYMBOL = "symbol"


@dataclass
class SearchResult:
    """Search result from any search type."""
    file_path: str
    line_number: Optional[int]
    content: str
    search_type: SearchType
    score: float  # Relevance score (0-1)
    context: Optional[str] = None  # Function/class context
    match_count: int = 1  # Number of matches in this location


# Type annotations for parameters
Query = Annotated[
    str,
    Field(
        description="The search pattern (supports regex for pattern search, natural language for semantic search)",
        min_length=1,
    ),
]

SearchPath = Annotated[
    str,
    Field(
        description="The directory to search in. Defaults to current directory.",
        default=".",
    ),
]

Strategy = Annotated[
    Literal["pattern", "ast", "semantic", "git", "all"],
    Field(
        description="Search strategy: pattern (regex/text), ast (code structure), semantic (vector), git (history), all (combined)",
        default="pattern",
    ),
]

Batch = Annotated[
    Optional[List[str]],
    Field(
        description="List of additional queries to search in parallel",
        default=None,
    ),
]

Include = Annotated[
    str,
    Field(
        description='File pattern to include (e.g. "*.js", "*.{ts,tsx}")',
        default="*",
    ),
]

ContextLines = Annotated[
    int,
    Field(
        description="Number of context lines around matches",
        default=2,
        ge=0,
        le=10,
    ),
]

Parallel = Annotated[
    bool,
    Field(
        description="Run searches in parallel for faster results",
        default=False,
    ),
]

MaxResults = Annotated[
    Optional[int],
    Field(
        description="Maximum number of results to return",
        default=None,
        gt=0,
    ),
]


class SearchParams(TypedDict):
    """Parameters for the unified search tool."""
    query: Query
    path: SearchPath
    strategy: Strategy
    batch: Batch
    include: Include
    context_lines: ContextLines
    parallel: Parallel
    max_results: MaxResults


# Legacy grep parameters for backward compatibility
Pattern = Annotated[
    str,
    Field(
        description="The regular expression pattern to search for in file contents",
        min_length=1,
    ),
]


class GrepToolParams(TypedDict):
    """Legacy parameters for grep tool compatibility."""
    pattern: Pattern
    path: SearchPath
    include: Include


@final
class UnifiedSearchTool(FilesystemBaseTool):
    """Unified search tool that combines multiple search strategies."""

    def __init__(
        self,
        permission_manager,
        project_manager: Optional[ProjectVectorManager] = None,
    ):
        """Initialize the unified search tool.

        Args:
            permission_manager: Permission manager for access control
            project_manager: Optional project manager for vector search
        """
        super().__init__(permission_manager)
        self.project_manager = project_manager

        # Initialize component tools
        self.grep_ast_tool = None
        self.git_search_tool = None
        self.vector_tool = None

        if AST_SEARCH_AVAILABLE:
            self.grep_ast_tool = ASTTool(permission_manager)

        if GIT_SEARCH_AVAILABLE:
            self.git_search_tool = GitSearchTool(permission_manager)

        if VECTOR_SEARCH_AVAILABLE and project_manager:
            self.vector_tool = VectorSearchTool(permission_manager, project_manager)

    @property
    @override
    def name(self) -> str:
        """Get the tool name."""
        return "search"

    @property
    @override
    def description(self) -> str:
        """Get the tool description."""
        return """Unified search tool that combines multiple search strategies.

Supports different search strategies:
- pattern: Fast regex/text search using ripgrep
- ast: AST-aware code structure search  
- semantic: Vector-based semantic similarity search
- git: Search through git history and commits
- all: Run all available strategies and combine results

Can batch multiple queries for comprehensive analysis.
Results are combined, deduplicated, and ranked by relevance.

Examples:
- search(query="TODO", strategy="pattern") - Find TODO comments
- search(query="error handling", strategy="semantic") - Find error handling code
- search(query="processPayment", strategy="ast") - Find function definitions
- search(query="bug fix", strategy="git") - Search git history
- search(query="auth", batch=["authentication", "authorize"], strategy="all") - Multi-query search"""

    def is_ripgrep_installed(self) -> bool:
        """Check if ripgrep (rg) is installed."""
        return shutil.which("rg") is not None

    async def run_ripgrep(
        self,
        pattern: str,
        path: str,
        tool_ctx: ToolContext,
        include_pattern: str | None = None,
    ) -> str:
        """Run ripgrep with the given parameters and return the results."""
        # Special case for tests: direct file path with include pattern that doesn't match
        if Path(path).is_file() and include_pattern and include_pattern != "*":
            if not fnmatch.fnmatch(Path(path).name, include_pattern):
                await tool_ctx.info(f"File does not match pattern '{include_pattern}': {path}")
                return f"File does not match pattern '{include_pattern}': {path}"

        cmd = ["rg", "--json", pattern]

        # Add path
        cmd.append(path)

        # Add include pattern if provided
        if include_pattern and include_pattern != "*":
            cmd.extend(["-g", include_pattern])

        await tool_ctx.info(f"Running ripgrep command: {shlex.join(cmd)}")

        try:
            # Execute ripgrep process
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0 and process.returncode != 1:
                # rg returns 1 when no matches are found, which is not an error
                await tool_ctx.error(f"ripgrep failed with exit code {process.returncode}: {stderr.decode()}")
                return f"Error executing ripgrep: {stderr.decode()}"

            # Parse the JSON output
            results = self.parse_ripgrep_json_output(stdout.decode())
            return results

        except Exception as e:
            await tool_ctx.error(f"Error running ripgrep: {str(e)}")
            return f"Error running ripgrep: {str(e)}"

    def parse_ripgrep_json_output(self, output: str) -> str:
        """Parse ripgrep JSON output and format it for human readability."""
        if not output.strip():
            return "No matches found."

        formatted_results = []
        file_results = {}

        for line in output.splitlines():
            if not line.strip():
                continue

            try:
                data = json.loads(line)

                if data.get("type") == "match":
                    path = data.get("data", {}).get("path", {}).get("text", "")
                    line_number = data.get("data", {}).get("line_number", 0)
                    line_text = data.get("data", {}).get("lines", {}).get("text", "").rstrip()

                    if path not in file_results:
                        file_results[path] = []

                    file_results[path].append((line_number, line_text))

            except json.JSONDecodeError as e:
                formatted_results.append(f"Error parsing JSON: {str(e)}")

        # Count total matches
        total_matches = sum(len(matches) for matches in file_results.values())
        total_files = len(file_results)

        if total_matches == 0:
            return "No matches found."

        formatted_results.append(
            f"Found {total_matches} matches in {total_files} file{'s' if total_files > 1 else ''}:"
        )
        formatted_results.append("")  # Empty line for readability

        # Format the results by file
        for file_path, matches in file_results.items():
            for line_number, line_text in matches:
                formatted_results.append(f"{file_path}:{line_number}: {line_text}")

        return "\n".join(formatted_results)

    async def fallback_grep(
        self,
        pattern: str,
        path: str,
        tool_ctx: ToolContext,
        include_pattern: str | None = None,
    ) -> str:
        """Fallback Python implementation when ripgrep is not available."""
        await tool_ctx.info("Using fallback Python implementation for grep")

        try:
            input_path = Path(path)

            # Find matching files
            matching_files: list[Path] = []

            # Process based on whether path is a file or directory
            if input_path.is_file():
                # Single file search - check file pattern match first
                if (
                    include_pattern is None
                    or include_pattern == "*"
                    or fnmatch.fnmatch(input_path.name, include_pattern)
                ):
                    matching_files.append(input_path)
                    await tool_ctx.info(f"Searching single file: {path}")
                else:
                    # File doesn't match the pattern, return immediately
                    await tool_ctx.info(f"File does not match pattern '{include_pattern}': {path}")
                    return f"File does not match pattern '{include_pattern}': {path}"
            elif input_path.is_dir():
                # Directory search - find all files
                await tool_ctx.info(f"Finding files in directory: {path}")

                # Keep track of allowed paths for filtering
                allowed_paths: set[str] = set()

                # Collect all allowed paths first for faster filtering
                for entry in input_path.rglob("*"):
                    entry_path = str(entry)
                    if self.is_path_allowed(entry_path):
                        allowed_paths.add(entry_path)

                # Find matching files efficiently
                for entry in input_path.rglob("*"):
                    entry_path = str(entry)
                    if entry_path in allowed_paths and entry.is_file():
                        if (
                            include_pattern is None
                            or include_pattern == "*"
                            or fnmatch.fnmatch(entry.name, include_pattern)
                        ):
                            matching_files.append(entry)

                await tool_ctx.info(f"Found {len(matching_files)} matching files")
            else:
                # This shouldn't happen if path exists
                await tool_ctx.error(f"Path is neither a file nor a directory: {path}")
                return f"Error: Path is neither a file nor a directory: {path}"

            # Report progress
            total_files = len(matching_files)
            if input_path.is_file():
                await tool_ctx.info(f"Searching file: {path}")
            else:
                await tool_ctx.info(f"Searching through {total_files} files in directory")

            # Set up for parallel processing
            results: list[str] = []
            files_processed = 0
            matches_found = 0
            batch_size = 20  # Process files in batches to avoid overwhelming the system

            # Use a semaphore to limit concurrent file operations
            semaphore = asyncio.Semaphore(10)

            # Create an async function to search a single file
            async def search_file(file_path: Path) -> list[str]:
                nonlocal files_processed, matches_found
                file_results: list[str] = []

                try:
                    async with semaphore:  # Limit concurrent operations
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                for line_num, line in enumerate(f, 1):
                                    if re.search(pattern, line):
                                        file_results.append(f"{file_path}:{line_num}: {line.rstrip()}")
                                        matches_found += 1
                            files_processed += 1
                        except UnicodeDecodeError:
                            # Skip binary files
                            files_processed += 1
                        except Exception as e:
                            await tool_ctx.warning(f"Error reading {file_path}: {str(e)}")
                except Exception as e:
                    await tool_ctx.warning(f"Error processing {file_path}: {str(e)}")

                return file_results

            # Process files in parallel batches
            for i in range(0, len(matching_files), batch_size):
                batch = matching_files[i : i + batch_size]
                batch_tasks = [search_file(file_path) for file_path in batch]

                # Report progress
                await tool_ctx.report_progress(i, total_files)

                # Wait for the batch to complete
                batch_results = await asyncio.gather(*batch_tasks)

                # Flatten and collect results
                for file_result in batch_results:
                    results.extend(file_result)

            # Final progress report
            await tool_ctx.report_progress(total_files, total_files)

            if not results:
                if input_path.is_file():
                    return f"No matches found for pattern '{pattern}' in file: {path}"
                else:
                    return f"No matches found for pattern '{pattern}' in files matching '{include_pattern or '*'}' in directory: {path}"

            await tool_ctx.info(
                f"Found {matches_found} matches in {files_processed} file{'s' if files_processed > 1 else ''}"
            )
            return (
                f"Found {matches_found} matches in {files_processed} file{'s' if files_processed > 1 else ''}:\n\n"
                + "\n".join(results)
            )
        except Exception as e:
            await tool_ctx.error(f"Error searching file contents: {str(e)}")
            return f"Error searching file contents: {str(e)}"

    def _analyze_pattern(self, pattern: str) -> Dict[str, bool]:
        """Analyze the pattern to determine optimal search strategies."""
        # Check if pattern looks like regex
        regex_chars = r"[.*+?^${}()|[\]\\]"
        has_regex = bool(re.search(regex_chars, pattern))

        # Check if pattern looks like a symbol name
        is_symbol = bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", pattern))

        # Check if pattern is natural language
        words = pattern.split()
        is_natural_language = len(words) > 2 and not has_regex

        return {
            "use_grep": True,  # Always useful
            "use_grep_ast": not has_regex,  # AST doesn't handle regex well
            "use_vector": is_natural_language or len(pattern) > 10,
            "use_git": True,  # Always check history
            "use_symbol": is_symbol or "def" in pattern or "class" in pattern,
        }

    async def _run_pattern_search(
        self, pattern: str, path: str, include: str, tool_ctx: ToolContext, max_results: Optional[int]
    ) -> List[SearchResult]:
        """Run pattern search using ripgrep or fallback."""
        try:
            if self.is_ripgrep_installed():
                await tool_ctx.info("Using ripgrep for pattern search")
                result = await self.run_ripgrep(pattern, path, tool_ctx, include)
            else:
                await tool_ctx.info("Using fallback implementation for pattern search")
                result = await self.fallback_grep(pattern, path, tool_ctx, include)

            results = []
            if "Found" in result and "matches" in result:
                lines = result.split("\n")
                for line in lines[2:]:  # Skip header
                    if ":" in line and line.strip():
                        try:
                            parts = line.split(":", 2)
                            if len(parts) >= 3:
                                results.append(
                                    SearchResult(
                                        file_path=parts[0],
                                        line_number=int(parts[1]),
                                        content=parts[2].strip(),
                                        search_type=SearchType.GREP,
                                        score=1.0,  # Exact matches get perfect score
                                    )
                                )
                                if max_results and len(results) >= max_results:
                                    break
                        except ValueError:
                            continue

            await tool_ctx.info(f"Pattern search found {len(results)} results")
            return results

        except Exception as e:
            await tool_ctx.error(f"Pattern search failed: {e}")
            return []

    async def _run_ast_search(
        self, pattern: str, path: str, tool_ctx: ToolContext, max_results: Optional[int]
    ) -> List[SearchResult]:
        """Run AST-aware search."""
        if not self.grep_ast_tool:
            return []

        try:
            result = await self.grep_ast_tool.call(
                tool_ctx.mcp_context,
                pattern=pattern,
                path=path,
                ignore_case=True,
                line_number=True,
            )

            results = []
            if result and not result.startswith("No matches"):
                current_file = None
                current_context = []

                for line in result.split("\n"):
                    if line.endswith(":") and "/" in line:
                        current_file = line[:-1]
                        current_context = []
                    elif current_file and ":" in line:
                        try:
                            # Try to parse line with number
                            parts = line.split(":", 1)
                            line_num = int(parts[0].strip())
                            content = parts[1].strip() if len(parts) > 1 else ""

                            results.append(
                                SearchResult(
                                    file_path=current_file,
                                    line_number=line_num,
                                    content=content,
                                    search_type=SearchType.GREP_AST,
                                    score=0.95,  # High score for AST matches
                                    context=(" > ".join(current_context) if current_context else None),
                                )
                            )

                            if max_results and len(results) >= max_results:
                                break
                        except ValueError:
                            # This might be context info
                            if line.strip():
                                current_context.append(line.strip())

            await tool_ctx.info(f"AST search found {len(results)} results")
            return results

        except Exception as e:
            await tool_ctx.error(f"AST search failed: {e}")
            return []

    async def _run_semantic_search(
        self, pattern: str, path: str, tool_ctx: ToolContext, max_results: Optional[int]
    ) -> List[SearchResult]:
        """Run semantic vector search."""
        if not self.vector_tool:
            return []

        try:
            # Determine search scope
            search_scope = "current" if path == "." else "all"

            result = await self.vector_tool.call(
                tool_ctx.mcp_context,
                query=pattern,
                limit=max_results or 50,
                score_threshold=0.3,
                search_scope=search_scope,
                include_content=True,
            )

            results = []
            if "Found" in result:
                # Parse vector search results
                lines = result.split("\n")
                current_file = None
                current_score = 0.0

                for line in lines:
                    if "Result" in line and "Score:" in line:
                        # Extract score and file
                        score_match = re.search(r"Score: ([\d.]+)%", line)
                        if score_match:
                            current_score = float(score_match.group(1)) / 100.0

                        file_match = re.search(r" - ([^\s]+)$", line)
                        if file_match:
                            current_file = file_match.group(1)

                    elif current_file and line.strip() and not line.startswith("-"):
                        # Content line
                        results.append(
                            SearchResult(
                                file_path=current_file,
                                line_number=None,
                                content=line.strip()[:200],  # Limit content length
                                search_type=SearchType.VECTOR,
                                score=current_score,
                            )
                        )

                        if max_results and len(results) >= max_results:
                            break

            await tool_ctx.info(f"Semantic search found {len(results)} results")
            return results

        except Exception as e:
            await tool_ctx.error(f"Semantic search failed: {e}")
            return []

    async def _run_git_search(
        self, pattern: str, path: str, tool_ctx: ToolContext, max_results: Optional[int]
    ) -> List[SearchResult]:
        """Run git history search."""
        if not self.git_search_tool:
            return []

        try:
            # Search in both content and commits
            max_per_type = (max_results or 50) // 2
            tasks = [
                self.git_search_tool.call(
                    tool_ctx.mcp_context,
                    pattern=pattern,
                    path=path,
                    search_type="content",
                    max_count=max_per_type,
                ),
                self.git_search_tool.call(
                    tool_ctx.mcp_context,
                    pattern=pattern,
                    path=path,
                    search_type="commits",
                    max_count=max_per_type,
                ),
            ]

            git_results = await asyncio.gather(*tasks, return_exceptions=True)

            results = []
            for _i, result in enumerate(git_results):
                if isinstance(result, Exception):
                    continue

                if "Found" in result:
                    # Parse git results
                    lines = result.split("\n")
                    for line in lines:
                        if ":" in line and line.strip():
                            parts = line.split(":", 2)
                            if len(parts) >= 2:
                                results.append(
                                    SearchResult(
                                        file_path=parts[0].strip(),
                                        line_number=None,
                                        content=(parts[-1].strip() if len(parts) > 2 else line),
                                        search_type=SearchType.GIT,
                                        score=0.8,  # Good score for git matches
                                    )
                                )

                                if max_results and len(results) >= max_results:
                                    break

            await tool_ctx.info(f"Git search found {len(results)} results")
            return results

        except Exception as e:
            await tool_ctx.error(f"Git search failed: {e}")
            return []

    async def _run_symbol_search(
        self, pattern: str, path: str, tool_ctx: ToolContext, max_results: Optional[int]
    ) -> List[SearchResult]:
        """Search for symbol definitions using grep with specific patterns."""
        try:
            # Create patterns for common symbol definitions
            symbol_patterns = [
                f"(def|class|function|func|fn)\\s+{pattern}",  # Python, JS, various
                f"(public|private|protected)?\\s*(static)?\\s*\\w+\\s+{pattern}\\s*\\(",  # Java/C++
                f"const\\s+{pattern}\\s*=",  # JS/TS const
                f"let\\s+{pattern}\\s*=",  # JS/TS let
                f"var\\s+{pattern}\\s*=",  # JS/TS var
            ]

            # Run pattern searches for each symbol pattern
            all_results = []
            max_per_pattern = (max_results or 50) // len(symbol_patterns)

            for sp in symbol_patterns:
                pattern_results = await self._run_pattern_search(
                    sp, path, "*", tool_ctx, max_per_pattern
                )
                # Convert to symbol type
                for result in pattern_results:
                    result.search_type = SearchType.SYMBOL
                    result.score = 0.98  # Very high score for symbol definitions
                all_results.extend(pattern_results)

            await tool_ctx.info(f"Symbol search found {len(all_results)} results")
            return all_results

        except Exception as e:
            await tool_ctx.error(f"Symbol search failed: {e}")
            return []

    def _deduplicate_results(self, all_results: List[SearchResult]) -> List[SearchResult]:
        """Deduplicate results, keeping the highest scoring version."""
        seen = {}

        for result in all_results:
            key = (result.file_path, result.line_number)

            if key not in seen or result.score > seen[key].score:
                seen[key] = result
            elif key in seen and result.context and not seen[key].context:
                # Add context if missing
                seen[key].context = result.context

        return list(seen.values())

    def _rank_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Rank results by relevance score and search type priority."""
        # Define search type priorities
        type_priority = {
            SearchType.SYMBOL: 5,
            SearchType.GREP: 4,
            SearchType.GREP_AST: 3,
            SearchType.GIT: 2,
            SearchType.VECTOR: 1,
        }

        # Sort by score (descending) and then by type priority
        results.sort(key=lambda r: (r.score, type_priority.get(r.search_type, 0)), reverse=True)

        return results

    def _format_results(
        self,
        query: str,
        results: List[SearchResult],
        results_by_type: Dict[SearchType, List[SearchResult]],
        search_time_ms: float,
        strategy: str,
    ) -> str:
        """Format search results for display."""
        output = []

        # Header
        output.append(f"=== Search Results ===")
        output.append(f"Query: '{query}'")
        output.append(f"Strategy: {strategy}")
        output.append(f"Total results: {len(results)}")
        output.append(f"Search time: {search_time_ms:.1f}ms")

        # Summary by type
        output.append("\nResults by type:")
        for search_type, type_results in results_by_type.items():
            if type_results:
                output.append(f"  {search_type.value}: {len(type_results)} matches")

        if not results:
            output.append("\nNo results found.")
            return "\n".join(output)

        # Group results by file
        results_by_file = {}
        for result in results:
            if result.file_path not in results_by_file:
                results_by_file[result.file_path] = []
            results_by_file[result.file_path].append(result)

        # Display results
        output.append(f"\n=== Results ({len(results)} total) ===\n")

        for file_path, file_results in results_by_file.items():
            output.append(f"{file_path}")
            output.append("-" * len(file_path))

            # Sort by line number
            file_results.sort(key=lambda r: r.line_number or 0)

            for result in file_results:
                # Format result line
                score_str = f"[{result.search_type.value} {result.score:.2f}]"

                if result.line_number:
                    output.append(f"  {result.line_number:>4}: {score_str} {result.content}")
                else:
                    output.append(f"       {score_str} {result.content}")

                # Add context if available
                if result.context:
                    output.append(f"         Context: {result.context}")

            output.append("")  # Empty line between files

        return "\n".join(output)

    async def run_unified_search(
        self,
        query: str,
        path: str,
        strategy: str,
        include: str,
        max_results: Optional[int],
        tool_ctx: ToolContext,
    ) -> str:
        """Run unified search with specified strategy."""
        import time
        start_time = time.time()

        await tool_ctx.info(f"Starting {strategy} search for '{query}' in {path}")

        # Determine which searches to run based on strategy
        search_tasks = []
        search_names = []

        if strategy == "pattern":
            search_tasks.append(self._run_pattern_search(query, path, include, tool_ctx, max_results))
            search_names.append("pattern")
        elif strategy == "ast":
            if self.grep_ast_tool:
                search_tasks.append(self._run_ast_search(query, path, tool_ctx, max_results))
                search_names.append("ast")
            else:
                await tool_ctx.warning("AST search not available, falling back to pattern search")
                search_tasks.append(self._run_pattern_search(query, path, include, tool_ctx, max_results))
                search_names.append("pattern")
        elif strategy == "semantic":
            if self.vector_tool:
                search_tasks.append(self._run_semantic_search(query, path, tool_ctx, max_results))
                search_names.append("semantic")
            else:
                await tool_ctx.warning("Semantic search not available, falling back to pattern search")
                search_tasks.append(self._run_pattern_search(query, path, include, tool_ctx, max_results))
                search_names.append("pattern")
        elif strategy == "git":
            if self.git_search_tool:
                search_tasks.append(self._run_git_search(query, path, tool_ctx, max_results))
                search_names.append("git")
            else:
                await tool_ctx.warning("Git search not available, falling back to pattern search")
                search_tasks.append(self._run_pattern_search(query, path, include, tool_ctx, max_results))
                search_names.append("pattern")
        elif strategy == "all":
            # Analyze pattern to determine best strategies
            pattern_analysis = self._analyze_pattern(query)
            
            if pattern_analysis["use_grep"]:
                search_tasks.append(self._run_pattern_search(query, path, include, tool_ctx, max_results))
                search_names.append("pattern")
            
            if pattern_analysis["use_grep_ast"] and self.grep_ast_tool:
                search_tasks.append(self._run_ast_search(query, path, tool_ctx, max_results))
                search_names.append("ast")
            
            if pattern_analysis["use_vector"] and self.vector_tool:
                search_tasks.append(self._run_semantic_search(query, path, tool_ctx, max_results))
                search_names.append("semantic")
            
            if pattern_analysis["use_git"] and self.git_search_tool:
                search_tasks.append(self._run_git_search(query, path, tool_ctx, max_results))
                search_names.append("git")
            
            if pattern_analysis["use_symbol"]:
                search_tasks.append(self._run_symbol_search(query, path, tool_ctx, max_results))
                search_names.append("symbol")

        await tool_ctx.info(f"Running {len(search_tasks)} search types: {', '.join(search_names)}")

        # Run all searches
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)

        # Collect all results
        all_results = []
        results_by_type = {}

        for search_type, results in zip(search_names, search_results):
            if isinstance(results, Exception):
                await tool_ctx.error(f"{search_type} search failed: {results}")
                results_by_type[SearchType(search_type)] = []
            else:
                # Map search names to SearchType enum
                search_type_enum = {
                    "pattern": SearchType.GREP,
                    "ast": SearchType.GREP_AST,
                    "semantic": SearchType.VECTOR,
                    "git": SearchType.GIT,
                    "symbol": SearchType.SYMBOL,
                }.get(search_type, SearchType.GREP)
                
                results_by_type[search_type_enum] = results
                all_results.extend(results)

        # Deduplicate and rank results
        unique_results = self._deduplicate_results(all_results)
        ranked_results = self._rank_results(unique_results)

        # Limit total results
        if max_results:
            final_results = ranked_results[:max_results]
        else:
            final_results = ranked_results

        # Calculate search time
        search_time = (time.time() - start_time) * 1000

        # Format output
        return self._format_results(
            query=query,
            results=final_results,
            results_by_type=results_by_type,
            search_time_ms=search_time,
            strategy=strategy,
        )

    @override
    async def call(
        self,
        ctx: MCPContext,
        **params: Unpack[Union[SearchParams, GrepToolParams]],
    ) -> str:
        """Execute the search tool with the given parameters."""
        tool_ctx = self.create_tool_context(ctx)

        # Handle both new and legacy parameter formats
        if "query" in params:
            # New unified search parameters
            query = params["query"]
            path = params.get("path", ".")
            strategy = params.get("strategy", "pattern")
            batch = params.get("batch")
            include = params.get("include", "*")
            context_lines = params.get("context_lines", 2)
            parallel = params.get("parallel", False)
            max_results = params.get("max_results")
        else:
            # Legacy grep parameters
            query = params.get("pattern")
            path = params.get("path", ".")
            strategy = "pattern"
            batch = None
            include = params.get("include", "*")
            context_lines = 2
            parallel = False
            max_results = None

        # Expand path (handles ~, $HOME, etc.)
        path = self.expand_path(path)

        # Validate required parameters
        if query is None:
            await tool_ctx.error("Parameter 'query' or 'pattern' is required but was None")
            return "Error: Parameter 'query' or 'pattern' is required but was None"

        # Validate path
        path_validation = self.validate_path(path)
        if path_validation.is_error:
            await tool_ctx.error(path_validation.error_message)
            return f"Error: {path_validation.error_message}"

        # Check if path is allowed
        allowed, error_msg = await self.check_path_allowed(path, tool_ctx)
        if not allowed:
            return error_msg

        # Check if path exists
        exists, error_msg = await self.check_path_exists(path, tool_ctx)
        if not exists:
            return error_msg

        # Handle batch queries
        if batch:
            # Run all queries including the main one
            all_queries = [query] + batch
            
            if parallel:
                # Run all queries in parallel
                await tool_ctx.info(f"Running {len(all_queries)} queries in parallel")
                tasks = [
                    self.run_unified_search(q, path, strategy, include, max_results, tool_ctx)
                    for q in all_queries
                ]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Combine results
                output = [f"=== Batch Search Results ({len(all_queries)} queries) ===\n"]
                for i, (q, result) in enumerate(zip(all_queries, batch_results)):
                    if isinstance(result, Exception):
                        output.append(f"Query {i+1} '{q}' failed: {result}\n")
                    else:
                        output.append(f"Query {i+1}: {result}\n")
                        output.append("="*80 + "\n")
                
                return "\n".join(output)
            else:
                # Run queries sequentially  
                await tool_ctx.info(f"Running {len(all_queries)} queries sequentially")
                output = [f"=== Batch Search Results ({len(all_queries)} queries) ===\n"]
                
                for i, q in enumerate(all_queries):
                    result = await self.run_unified_search(q, path, strategy, include, max_results, tool_ctx)
                    output.append(f"Query {i+1}: {result}\n")
                    output.append("="*80 + "\n")
                
                return "\n".join(output)
        else:
            # Single query
            result = await self.run_unified_search(query, path, strategy, include, max_results, tool_ctx)
            return truncate_response(
                result,
                max_tokens=25000,
                truncation_message="\n\n[Search results truncated due to token limit. Use more specific patterns or limit max_results.]",
            )

    @override
    def register(self, mcp_server: FastMCP) -> None:
        """Register this search tool with the MCP server."""
        tool_self = self

        @mcp_server.tool(name=self.name, description=self.description)
        async def search(
            ctx: MCPContext,
            query: Query,
            path: SearchPath = ".",
            strategy: Strategy = "pattern",
            batch: Batch = None,
            include: Include = "*",
            context_lines: ContextLines = 2,
            parallel: Parallel = False,
            max_results: MaxResults = None,
        ) -> str:
            return await tool_self.call(
                ctx,
                query=query,
                path=path,
                strategy=strategy,
                batch=batch,
                include=include,
                context_lines=context_lines,
                parallel=parallel,
                max_results=max_results,
            )


# Legacy alias for backward compatibility
class Grep(UnifiedSearchTool):
    """Legacy grep tool - alias for unified search with pattern strategy."""

    @property
    @override
    def name(self) -> str:
        """Get the tool name."""
        return "grep"

    @property
    @override
    def description(self) -> str:
        """Get the tool description."""
        return """Fast content search tool that works with any codebase size.
Searches file contents using regular expressions.
Supports full regex syntax (eg. "log.*Error", "function\\s+\\w+", etc.).
Filter files by pattern with the include parameter (eg. "*.js", "*.{ts,tsx}").
Returns matching file paths sorted by modification time.
Use this tool when you need to find files containing specific patterns.
When you are doing an open ended search that may require multiple rounds of globbing and grepping, use the Agent tool instead."""

    @override
    def register(self, mcp_server: FastMCP) -> None:
        """Register this grep tool with the MCP server."""
        tool_self = self

        @mcp_server.tool(name=self.name, description=self.description)
        async def grep(
            ctx: MCPContext,
            pattern: Pattern,
            path: SearchPath = ".",
            include: Include = "*",
        ) -> str:
            # Map legacy parameters to new format
            return await tool_self.call(ctx, pattern=pattern, path=path, include=include)


# Factory functions for easy instantiation
def create_unified_search_tool(permission_manager=None, project_manager=None):
    """Create a unified search tool instance."""
    if permission_manager is None:
        from hanzo_mcp.tools.common.permissions import PermissionManager
        permission_manager = PermissionManager()
    
    return UnifiedSearchTool(permission_manager, project_manager)


def create_grep_tool(permission_manager=None):
    """Create a legacy grep tool instance.""" 
    if permission_manager is None:
        from hanzo_mcp.tools.common.permissions import PermissionManager
        permission_manager = PermissionManager()
    
    return Grep(permission_manager)