"""Node management tool for hanzo-node operations."""

import asyncio
import json
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, final, override

import httpx
from mcp.server import FastMCP
from mcp.server.fastmcp import Context as MCPContext

from hanzo_mcp.tools.common.base import BaseTool
from hanzo_mcp.tools.common.context import create_tool_context

logger = logging.getLogger(__name__)

# Default hanzo-node configuration
DEFAULT_NODE_CONFIG = {
    "host": "localhost",
    "port": 3690,
    "db_path": "~/.hanzo/lancedb",
    "models_path": "~/.hanzo/models",
    "log_level": "info",
    "embedding_model": "text-embedding-3-small",
    "embedding_dimensions": 1536
}


@final
class NodeTool(BaseTool):
    """Tool for managing local hanzo-node instance.
    
    This tool provides management capabilities for the local hanzo-node:
    - Download and install hanzo-node
    - Configure node settings via ~/.hanzo
    - Start/stop/restart node
    - Check node status and health
    - Manage vector store (LanceDB)
    - Download and load models
    - View logs and diagnostics
    """
    
    def __init__(self):
        """Initialize node management tool."""
        self.hanzo_dir = Path.home() / ".hanzo"
        self.config_file = self.hanzo_dir / "node_config.json"
        self.models_dir = self.hanzo_dir / "models"
        self.logs_dir = self.hanzo_dir / "logs"
        self.lancedb_dir = self.hanzo_dir / "lancedb"
        
        # Ensure directories exist
        for directory in [self.hanzo_dir, self.models_dir, self.logs_dir, self.lancedb_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Initialize config if it doesn't exist
        self._ensure_config()
        
    def _ensure_config(self) -> None:
        """Ensure node configuration exists."""
        if not self.config_file.exists():
            config = DEFAULT_NODE_CONFIG.copy()
            # Expand paths
            config["db_path"] = str(self.lancedb_dir)
            config["models_path"] = str(self.models_dir)
            self._save_config(config)
            
    def _load_config(self) -> Dict[str, Any]:
        """Load node configuration."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return DEFAULT_NODE_CONFIG.copy()
            
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save node configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
    async def _is_node_running(self, host: str = "localhost", port: int = 3690) -> bool:
        """Check if hanzo-node is running."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"http://{host}:{port}/health")
                return response.status_code == 200
        except Exception:
            return False
            
    async def _find_node_executable(self) -> Optional[Path]:
        """Find hanzo-node executable."""
        # Check common locations
        possible_paths = [
            Path.home() / ".hanzo" / "bin" / "hanzo-node",
            Path("/usr/local/bin/hanzo-node"),
            Path("/opt/hanzo/bin/hanzo-node"),
            # Development paths
            Path.home() / "work" / "hanzo" / "node" / "apps" / "hanzo-node" / "target" / "release" / "hanzo-node",
            Path.home() / "work" / "hanzo" / "target" / "release" / "hanzo-node",
        ]
        
        # Also check PATH
        if shutil.which("hanzo-node"):
            possible_paths.append(Path(shutil.which("hanzo-node")))
            
        for path in possible_paths:
            if path.exists() and path.is_file():
                return path
                
        return None
        
    async def _download_node(self, tool_ctx) -> bool:
        """Download hanzo-node if not available."""
        await tool_ctx.info("Downloading hanzo-node...")
        
        # For now, we'll build from source if available
        source_dir = Path.home() / "work" / "hanzo" / "node" / "apps" / "hanzo-node"
        if source_dir.exists():
            await tool_ctx.info("Building hanzo-node from source...")
            try:
                # Build the project
                result = subprocess.run(
                    ["cargo", "build", "--release"],
                    cwd=source_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes
                )
                
                if result.returncode == 0:
                    # Copy binary to hanzo directory
                    source_binary = source_dir / "target" / "release" / "hanzo-node"
                    target_binary = self.hanzo_dir / "bin" / "hanzo-node"
                    target_binary.parent.mkdir(parents=True, exist_ok=True)
                    
                    if source_binary.exists():
                        shutil.copy2(source_binary, target_binary)
                        target_binary.chmod(0o755)
                        await tool_ctx.info(f"Built and installed hanzo-node to {target_binary}")
                        return True
                    else:
                        await tool_ctx.error("Build succeeded but binary not found")
                        return False
                else:
                    await tool_ctx.error(f"Build failed: {result.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                await tool_ctx.error("Build timed out after 5 minutes")
                return False
            except Exception as e:
                await tool_ctx.error(f"Build error: {e}")
                return False
        else:
            await tool_ctx.warning("Source code not found. Manual installation required.")
            await tool_ctx.info("To install hanzo-node manually:")
            await tool_ctx.info("1. Download from releases or build from source")
            await tool_ctx.info("2. Place binary at ~/.hanzo/bin/hanzo-node")
            await tool_ctx.info("3. Run 'node(action=\"status\")' to verify")
            return False

    @property
    @override
    def name(self) -> str:
        """Get the tool name."""
        return "node"
        
    @property
    @override
    def description(self) -> str:
        """Get the tool description."""
        return """Manage local hanzo-node instance.

This tool provides comprehensive management of your local hanzo-node:

Configuration:
- Configure node settings via ~/.hanzo/node_config.json
- Set embedding models, database paths, ports
- Manage authentication and security settings

Lifecycle:
- Install/download hanzo-node if not available
- Start, stop, restart the node process
- Check node status and health
- View logs and diagnostics

Data Management:
- Manage vector store (LanceDB) location and settings
- Download and configure ML models
- Backup and restore node data
- Clear caches and temporary files

Examples:
node(action="status")  # Check if node is running
node(action="start")   # Start the node
node(action="stop")    # Stop the node
node(action="restart") # Restart the node
node(action="config", key="port", value="3691")  # Update config
node(action="logs")    # View recent logs
node(action="models")  # List available models
node(action="install") # Install/build hanzo-node
"""

    @override
    async def call(
        self,
        ctx: MCPContext,
        action: str,
        key: Optional[str] = None,
        value: Optional[str] = None,
        force: bool = False,
        **kwargs
    ) -> str:
        """Execute node management operations.
        
        Args:
            ctx: MCP context
            action: Action to perform (status, start, stop, restart, config, logs, models, install)
            key: Configuration key (for config action)
            value: Configuration value (for config action)
            force: Force action without confirmation
            **kwargs: Additional action-specific parameters
            
        Returns:
            Operation result or status information
        """
        tool_ctx = create_tool_context(ctx)
        await tool_ctx.set_tool_info(self.name)
        
        if action == "status":
            return await self._handle_status(tool_ctx)
        elif action == "start":
            return await self._handle_start(tool_ctx, force)
        elif action == "stop":
            return await self._handle_stop(tool_ctx, force)
        elif action == "restart":
            return await self._handle_restart(tool_ctx, force)
        elif action == "config":
            return await self._handle_config(tool_ctx, key, value)
        elif action == "logs":
            return await self._handle_logs(tool_ctx, kwargs.get("lines", 50))
        elif action == "models":
            return await self._handle_models(tool_ctx)
        elif action == "install":
            return await self._handle_install(tool_ctx, force)
        elif action == "clean":
            return await self._handle_clean(tool_ctx, force)
        else:
            return f"Unknown action: {action}. Available actions: status, start, stop, restart, config, logs, models, install, clean"
            
    async def _handle_status(self, tool_ctx) -> str:
        """Handle status check."""
        config = self._load_config()
        host = config.get("host", "localhost")
        port = config.get("port", 3690)
        
        status_info = [f"Hanzo Node Status"]
        status_info.append(f"Configuration: {self.config_file}")
        status_info.append(f"Expected URL: http://{host}:{port}")
        
        # Check if node is running
        is_running = await self._is_node_running(host, port)
        status_info.append(f"Running: {is_running}")
        
        # Check for executable
        executable = await self._find_node_executable()
        if executable:
            status_info.append(f"Executable: {executable}")
        else:
            status_info.append("Executable: Not found")
            
        # Check directories
        status_info.append(f"Data directory: {self.hanzo_dir}")
        status_info.append(f"Models directory: {self.models_dir} ({len(list(self.models_dir.glob('*')))} files)")
        status_info.append(f"LanceDB directory: {self.lancedb_dir} ({len(list(self.lancedb_dir.glob('*')))} files)")
        
        # Check config
        status_info.append(f"Configured port: {port}")
        status_info.append(f"Configured host: {host}")
        status_info.append(f"DB path: {config.get('db_path', 'Not set')}")
        status_info.append(f"Models path: {config.get('models_path', 'Not set')}")
        
        return "\n".join(status_info)
        
    async def _handle_start(self, tool_ctx, force: bool) -> str:
        """Handle node start."""
        config = self._load_config()
        host = config.get("host", "localhost")
        port = config.get("port", 3690)
        
        # Check if already running
        if await self._is_node_running(host, port):
            return f"Hanzo node is already running on {host}:{port}"
            
        # Find executable
        executable = await self._find_node_executable()
        if not executable:
            return "Hanzo node executable not found. Run node(action=\"install\") first."
            
        await tool_ctx.info(f"Starting hanzo-node on {host}:{port}...")
        
        try:
            # Prepare environment and arguments
            env = os.environ.copy()
            env["HANZO_CONFIG"] = str(self.config_file)
            
            # Start the process in background
            process = subprocess.Popen(
                [str(executable), "--config", str(self.config_file)],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Wait a moment and check if it started successfully
            await asyncio.sleep(2)
            
            if await self._is_node_running(host, port):
                return f"Successfully started hanzo-node on {host}:{port} (PID: {process.pid})"
            else:
                # Process might have failed
                return_code = process.poll()
                if return_code is not None:
                    _, stderr = process.communicate()
                    return f"Failed to start hanzo-node (exit code {return_code}): {stderr.decode()}"
                else:
                    return f"Started hanzo-node process (PID: {process.pid}) but health check failed"
                    
        except Exception as e:
            return f"Error starting hanzo-node: {e}"
            
    async def _handle_stop(self, tool_ctx, force: bool) -> str:
        """Handle node stop."""
        config = self._load_config()
        host = config.get("host", "localhost")
        port = config.get("port", 3690)
        
        # Check if running
        if not await self._is_node_running(host, port):
            return "Hanzo node is not running"
            
        await tool_ctx.info("Stopping hanzo-node...")
        
        try:
            # Try graceful shutdown via API first
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    response = await client.post(f"http://{host}:{port}/api/shutdown")
                    if response.status_code == 200:
                        # Wait for shutdown
                        await asyncio.sleep(2)
                        if not await self._is_node_running(host, port):
                            return "Successfully stopped hanzo-node"
                except Exception:
                    pass
                    
            # If graceful shutdown failed, try finding and killing the process
            if force:
                try:
                    # Find processes by name
                    result = subprocess.run(
                        ["pgrep", "-f", "hanzo-node"],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0 and result.stdout.strip():
                        pids = result.stdout.strip().split('\n')
                        for pid in pids:
                            subprocess.run(["kill", "-TERM", pid])
                            
                        await asyncio.sleep(2)
                        if not await self._is_node_running(host, port):
                            return f"Force stopped hanzo-node (killed {len(pids)} processes)"
                        else:
                            # Try SIGKILL
                            for pid in pids:
                                subprocess.run(["kill", "-KILL", pid])
                            return f"Force killed hanzo-node processes"
                except Exception as e:
                    return f"Error force stopping: {e}"
            else:
                return "Graceful shutdown failed. Use force=true for forceful shutdown."
                
        except Exception as e:
            return f"Error stopping hanzo-node: {e}"
            
    async def _handle_restart(self, tool_ctx, force: bool) -> str:
        """Handle node restart."""
        stop_result = await self._handle_stop(tool_ctx, force)
        await asyncio.sleep(1)
        start_result = await self._handle_start(tool_ctx, force)
        return f"Restart: {stop_result} -> {start_result}"
        
    async def _handle_config(self, tool_ctx, key: Optional[str], value: Optional[str]) -> str:
        """Handle configuration management."""
        config = self._load_config()
        
        if key is None:
            # Show current config
            formatted_config = json.dumps(config, indent=2)
            return f"Current configuration:\n{formatted_config}"
            
        if value is None:
            # Show specific key
            if key in config:
                return f"{key}: {config[key]}"
            else:
                return f"Configuration key '{key}' not found"
                
        # Update configuration
        old_value = config.get(key, "Not set")
        config[key] = value
        
        # Validate important settings
        if key == "port":
            try:
                port = int(value)
                if not (1024 <= port <= 65535):
                    return "Error: Port must be between 1024 and 65535"
            except ValueError:
                return "Error: Port must be a number"
                
        # Save updated config
        self._save_config(config)
        
        await tool_ctx.info(f"Updated {key}: {old_value} -> {value}")
        return f"Configuration updated: {key} = {value}\nRestart required for changes to take effect."
        
    async def _handle_logs(self, tool_ctx, lines: int = 50) -> str:
        """Handle log viewing."""
        log_file = self.logs_dir / "hanzo-node.log"
        
        if not log_file.exists():
            return "No log file found. Node may not have been started yet."
            
        try:
            # Read last N lines
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
            if not recent_lines:
                return "Log file is empty"
                
            log_content = ''.join(recent_lines)
            return f"Last {len(recent_lines)} lines from hanzo-node.log:\n{log_content}"
            
        except Exception as e:
            return f"Error reading log file: {e}"
            
    async def _handle_models(self, tool_ctx) -> str:
        """Handle model management."""
        models_info = [f"Models directory: {self.models_dir}"]
        
        # List model files
        model_files = list(self.models_dir.glob("*"))
        if model_files:
            models_info.append(f"\nFound {len(model_files)} model files:")
            for model_file in sorted(model_files):
                size_mb = model_file.stat().st_size / (1024 * 1024)
                models_info.append(f"  {model_file.name} ({size_mb:.1f} MB)")
        else:
            models_info.append("\nNo model files found")
            
        # Show config
        config = self._load_config()
        embedding_model = config.get("embedding_model", "Not set")
        models_info.append(f"\nConfigured embedding model: {embedding_model}")
        
        return "\n".join(models_info)
        
    async def _handle_install(self, tool_ctx, force: bool) -> str:
        """Handle node installation."""
        # Check if already exists
        existing = await self._find_node_executable()
        if existing and not force:
            return f"Hanzo node already installed at {existing}. Use force=true to reinstall."
            
        # Attempt download/build
        success = await self._download_node(tool_ctx)
        if success:
            return "Successfully installed hanzo-node"
        else:
            return "Failed to install hanzo-node. See logs above for details."
            
    async def _handle_clean(self, tool_ctx, force: bool) -> str:
        """Handle cleanup operations."""
        if not force:
            return "Clean operation requires force=true. This will remove logs and temporary files."
            
        await tool_ctx.info("Cleaning hanzo-node data...")
        
        cleaned = []
        
        # Clean logs
        if self.logs_dir.exists():
            for log_file in self.logs_dir.glob("*.log"):
                log_file.unlink()
                cleaned.append(f"Removed log: {log_file.name}")
                
        # Clean temporary files
        temp_patterns = ["*.tmp", "*.lock", "*.pid"]
        for pattern in temp_patterns:
            for temp_file in self.hanzo_dir.glob(pattern):
                temp_file.unlink()
                cleaned.append(f"Removed temp file: {temp_file.name}")
                
        if cleaned:
            return f"Cleaned {len(cleaned)} files:\n" + "\n".join(cleaned)
        else:
            return "No files to clean"

    @override
    def register(self, mcp_server: FastMCP) -> None:
        """Register this tool with the MCP server."""
        tool_self = self
        
        @mcp_server.tool(name=self.name, description=self.description)
        async def node(
            ctx: MCPContext,
            action: str,
            key: Optional[str] = None,
            value: Optional[str] = None,
            force: bool = False,
        ) -> str:
            return await tool_self.call(
                ctx,
                action=action,
                key=key,
                value=value,
                force=force,
            )