"""Run tool for command execution with automatic backgrounding."""

from typing import Optional, override
from mcp.server import FastMCP
from mcp.server.fastmcp import Context as MCPContext

from hanzo_mcp.tools.shell.zsh_tool import ShellTool


class RunTool(ShellTool):
    """Tool for running commands with automatic backgrounding (alias of shell tool)."""

    name = "run"

    def register(self, server: FastMCP) -> None:
        """Register the tool with the MCP server."""
        tool_self = self

        @server.tool(name=self.name, description=self.description)
        async def run(
            ctx: MCPContext,
            command: str,
            cwd: Optional[str] = None,
            env: Optional[dict[str, str]] = None,
            timeout: Optional[int] = None,
        ) -> str:
            return await tool_self.run(ctx, command=command, cwd=cwd, env=env, timeout=timeout)

    @property
    @override
    def description(self) -> str:
        """Get the tool description."""
        return """Execute shell commands with automatic backgrounding for long-running processes.

Automatically selects the best available shell:
- Zsh if available (with .zshrc)
- User's preferred shell ($SHELL)  
- Bash as fallback

Commands that run for more than 2 minutes will automatically continue in the background.
You can check their status and logs using the 'process' tool.

Usage:
run "ls -la"
run "python server.py"  # Auto-backgrounds after 2 minutes
run "git status && git diff"
run "npm run dev" --cwd ./frontend  # Auto-backgrounds if needed"""

    @override
    def get_tool_name(self) -> str:
        """Get the tool name."""
        return "run"


# Create instance
run_tool = RunTool()