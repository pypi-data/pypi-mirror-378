"""Enhanced Language Server Protocol (LSP) implementation with full protocol support.

This module provides a complete LSP client implementation with support for
all major programming languages including C, C++, Go, JavaScript, TypeScript,
Rust, Zig, and more.
"""

import os
import sys
import json
import asyncio
import logging
import subprocess
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from hanzo_mcp.types import MCPResourceDocument
from hanzo_mcp.tools.common.base import BaseTool


class MessageType(Enum):
    """LSP message types."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"


@dataclass
class LSPMessage:
    """Represents an LSP message."""
    type: MessageType
    id: Optional[int] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


@dataclass
class Position:
    """LSP position in a document."""
    line: int
    character: int
    
    def to_dict(self) -> Dict[str, int]:
        return {"line": self.line, "character": self.character}


@dataclass
class Range:
    """LSP range in a document."""
    start: Position
    end: Position
    
    def to_dict(self) -> Dict[str, Any]:
        return {"start": self.start.to_dict(), "end": self.end.to_dict()}


@dataclass
class Location:
    """LSP location."""
    uri: str
    range: Range
    
    def to_dict(self) -> Dict[str, Any]:
        return {"uri": self.uri, "range": self.range.to_dict()}


# Enhanced LSP server configurations with compilation support
ENHANCED_LSP_SERVERS = {
    "c": {
        "name": "clangd",
        "install_cmd": {
            "darwin": ["brew", "install", "llvm"],
            "linux": ["sudo", "apt-get", "install", "-y", "clangd"],
        },
        "check_cmd": ["clangd", "--version"],
        "start_cmd": ["clangd", "--background-index"],
        "root_markers": ["compile_commands.json", "CMakeLists.txt", ".clangd"],
        "file_extensions": [".c", ".h"],
        "compile_cmd": ["clang", "-o", "{output}", "{input}"],
        "run_cmd": ["./{output}"],
        "capabilities": [
            "definition", "references", "rename", "diagnostics",
            "hover", "completion", "formatting", "code_actions"
        ],
    },
    "cpp": {
        "name": "clangd",
        "install_cmd": {
            "darwin": ["brew", "install", "llvm"],
            "linux": ["sudo", "apt-get", "install", "-y", "clangd"],
        },
        "check_cmd": ["clangd", "--version"],
        "start_cmd": ["clangd", "--background-index"],
        "root_markers": ["compile_commands.json", "CMakeLists.txt", ".clangd"],
        "file_extensions": [".cpp", ".cc", ".cxx", ".hpp", ".hxx"],
        "compile_cmd": ["clang++", "-std=c++17", "-o", "{output}", "{input}"],
        "run_cmd": ["./{output}"],
        "capabilities": [
            "definition", "references", "rename", "diagnostics",
            "hover", "completion", "formatting", "code_actions"
        ],
    },
    "go": {
        "name": "gopls",
        "install_cmd": {
            "all": ["go", "install", "golang.org/x/tools/gopls@latest"],
        },
        "check_cmd": ["gopls", "version"],
        "start_cmd": ["gopls", "serve"],
        "root_markers": ["go.mod", "go.sum"],
        "file_extensions": [".go"],
        "compile_cmd": ["go", "build", "-o", "{output}", "{input}"],
        "run_cmd": ["./{output}"],
        "capabilities": [
            "definition", "references", "rename", "diagnostics",
            "hover", "completion", "formatting", "code_actions",
            "implementation", "type_definition"
        ],
    },
    "javascript": {
        "name": "typescript-language-server",
        "install_cmd": {
            "all": ["npm", "install", "-g", "typescript", "typescript-language-server"],
        },
        "check_cmd": ["typescript-language-server", "--version"],
        "start_cmd": ["typescript-language-server", "--stdio"],
        "root_markers": ["package.json", "tsconfig.json", "jsconfig.json"],
        "file_extensions": [".js", ".jsx", ".mjs"],
        "run_cmd": ["node", "{input}"],
        "capabilities": [
            "definition", "references", "rename", "diagnostics",
            "hover", "completion", "formatting", "code_actions"
        ],
    },
    "typescript": {
        "name": "typescript-language-server",
        "install_cmd": {
            "all": ["npm", "install", "-g", "typescript", "typescript-language-server"],
        },
        "check_cmd": ["typescript-language-server", "--version"],
        "start_cmd": ["typescript-language-server", "--stdio"],
        "root_markers": ["tsconfig.json", "package.json"],
        "file_extensions": [".ts", ".tsx"],
        "compile_cmd": ["tsc", "{input}", "--outFile", "{output}.js"],
        "run_cmd": ["node", "{output}.js"],
        "capabilities": [
            "definition", "references", "rename", "diagnostics",
            "hover", "completion", "formatting", "code_actions",
            "implementation", "type_definition"
        ],
    },
    "rust": {
        "name": "rust-analyzer",
        "install_cmd": {
            "all": ["rustup", "component", "add", "rust-analyzer"],
        },
        "check_cmd": ["rust-analyzer", "--version"],
        "start_cmd": ["rust-analyzer"],
        "root_markers": ["Cargo.toml"],
        "file_extensions": [".rs"],
        "compile_cmd": ["rustc", "-o", "{output}", "{input}"],
        "run_cmd": ["./{output}"],
        "capabilities": [
            "definition", "references", "rename", "diagnostics",
            "hover", "completion", "formatting", "code_actions",
            "inlay_hints", "implementation", "type_definition"
        ],
    },
    "zig": {
        "name": "zls",
        "install_cmd": {
            "darwin": ["brew", "install", "zls"],
            "linux": ["wget", "-O", "/tmp/zls.tar.gz", 
                     "https://github.com/zigtools/zls/releases/latest/download/zls-linux-x86_64.tar.gz",
                     "&&", "tar", "-xvf", "/tmp/zls.tar.gz", "-C", "/usr/local/bin"],
        },
        "check_cmd": ["zls", "--version"],
        "start_cmd": ["zls"],
        "root_markers": ["build.zig", "build.zig.zon"],
        "file_extensions": [".zig"],
        "compile_cmd": ["zig", "build-exe", "{input}", "-femit-bin={output}"],
        "run_cmd": ["./{output}"],
        "capabilities": [
            "definition", "references", "rename", "diagnostics",
            "hover", "completion", "formatting", "code_actions",
            "semantic_tokens"
        ],
    },
    "python": {
        "name": "pylsp",
        "install_cmd": {
            "all": ["pip", "install", "python-lsp-server[all]"],
        },
        "check_cmd": ["pylsp", "--version"],
        "start_cmd": ["pylsp"],
        "root_markers": ["pyproject.toml", "setup.py", "requirements.txt"],
        "file_extensions": [".py"],
        "run_cmd": ["python", "{input}"],
        "capabilities": [
            "definition", "references", "rename", "diagnostics",
            "hover", "completion", "formatting", "code_actions"
        ],
    },
}


class LSPClient:
    """Full LSP client implementation."""
    
    def __init__(self, language: str, root_uri: str):
        self.language = language
        self.root_uri = root_uri
        self.config = ENHANCED_LSP_SERVERS[language]
        self.process: Optional[asyncio.subprocess.Process] = None
        self.request_id = 0
        self.pending_requests: Dict[int, asyncio.Future] = {}
        self.initialized = False
        self.logger = logging.getLogger(f"LSP.{language}")
        
    async def start(self) -> bool:
        """Start the LSP server process."""
        try:
            self.process = await asyncio.create_subprocess_exec(
                *self.config["start_cmd"],
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.root_uri,
            )
            
            # Start message reader
            asyncio.create_task(self._read_messages())
            
            # Initialize
            await self.initialize()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start LSP: {e}")
            return False
    
    async def initialize(self):
        """Send initialize request."""
        params = {
            "processId": os.getpid(),
            "clientInfo": {
                "name": "hanzo-mcp",
                "version": "0.8.11"
            },
            "locale": "en",
            "rootPath": self.root_uri,
            "rootUri": f"file://{self.root_uri}",
            "capabilities": {
                "workspace": {
                    "applyEdit": True,
                    "workspaceEdit": {
                        "documentChanges": True,
                        "resourceOperations": ["create", "rename", "delete"],
                    },
                    "didChangeConfiguration": {"dynamicRegistration": True},
                    "symbol": {"dynamicRegistration": True},
                },
                "textDocument": {
                    "synchronization": {
                        "dynamicRegistration": True,
                        "willSave": True,
                        "willSaveWaitUntil": True,
                        "didSave": True,
                    },
                    "completion": {
                        "dynamicRegistration": True,
                        "contextSupport": True,
                        "completionItem": {
                            "snippetSupport": True,
                            "commitCharactersSupport": True,
                            "documentationFormat": ["markdown", "plaintext"],
                        },
                    },
                    "hover": {
                        "dynamicRegistration": True,
                        "contentFormat": ["markdown", "plaintext"],
                    },
                    "signatureHelp": {"dynamicRegistration": True},
                    "definition": {"dynamicRegistration": True},
                    "references": {"dynamicRegistration": True},
                    "documentHighlight": {"dynamicRegistration": True},
                    "documentSymbol": {"dynamicRegistration": True},
                    "codeAction": {"dynamicRegistration": True},
                    "codeLens": {"dynamicRegistration": True},
                    "formatting": {"dynamicRegistration": True},
                    "rangeFormatting": {"dynamicRegistration": True},
                    "onTypeFormatting": {"dynamicRegistration": True},
                    "rename": {"dynamicRegistration": True, "prepareSupport": True},
                    "documentLink": {"dynamicRegistration": True},
                },
            },
        }
        
        result = await self.send_request("initialize", params)
        
        if result:
            # Send initialized notification
            await self.send_notification("initialized", {})
            self.initialized = True
            
        return result
    
    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Send request and wait for response."""
        self.request_id += 1
        request_id = self.request_id
        
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }
        
        # Create future for response
        future = asyncio.get_event_loop().create_future()
        self.pending_requests[request_id] = future
        
        # Send request
        await self._send_message(request)
        
        # Wait for response
        try:
            result = await asyncio.wait_for(future, timeout=10.0)
            return result
        except asyncio.TimeoutError:
            self.logger.error(f"Request {method} timed out")
            del self.pending_requests[request_id]
            return None
    
    async def send_notification(self, method: str, params: Optional[Dict[str, Any]] = None):
        """Send notification (no response expected)."""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
        }
        
        await self._send_message(notification)
    
    async def _send_message(self, message: Dict[str, Any]):
        """Send message to LSP server."""
        if not self.process or self.process.returncode is not None:
            return
        
        content = json.dumps(message)
        content_bytes = content.encode("utf-8")
        
        header = f"Content-Length: {len(content_bytes)}\r\n\r\n"
        full_message = header.encode("utf-8") + content_bytes
        
        self.process.stdin.write(full_message)
        await self.process.stdin.drain()
    
    async def _read_messages(self):
        """Read messages from LSP server."""
        buffer = b""
        
        while self.process and self.process.returncode is None:
            try:
                chunk = await self.process.stdout.read(1024)
                if not chunk:
                    break
                    
                buffer += chunk
                
                # Parse messages
                while True:
                    message, remaining = self._parse_message(buffer)
                    if not message:
                        break
                        
                    buffer = remaining
                    await self._handle_message(message)
                    
            except Exception as e:
                self.logger.error(f"Error reading messages: {e}")
                break
    
    def _parse_message(self, buffer: bytes) -> Tuple[Optional[Dict[str, Any]], bytes]:
        """Parse LSP message from buffer."""
        # Look for Content-Length header
        header_end = buffer.find(b"\r\n\r\n")
        if header_end == -1:
            return None, buffer
        
        header = buffer[:header_end].decode("utf-8")
        
        # Parse content length
        content_length = None
        for line in header.split("\r\n"):
            if line.startswith("Content-Length:"):
                content_length = int(line.split(":")[1].strip())
                break
        
        if not content_length:
            return None, buffer
        
        # Check if we have full message
        message_start = header_end + 4
        message_end = message_start + content_length
        
        if len(buffer) < message_end:
            return None, buffer
        
        # Parse message
        message_bytes = buffer[message_start:message_end]
        try:
            message = json.loads(message_bytes.decode("utf-8"))
            return message, buffer[message_end:]
        except json.JSONDecodeError:
            return None, buffer[message_end:]
    
    async def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming LSP message."""
        if "id" in message and "result" in message:
            # Response to our request
            request_id = message["id"]
            if request_id in self.pending_requests:
                future = self.pending_requests.pop(request_id)
                future.set_result(message.get("result"))
                
        elif "id" in message and "error" in message:
            # Error response
            request_id = message["id"]
            if request_id in self.pending_requests:
                future = self.pending_requests.pop(request_id)
                future.set_exception(Exception(message["error"]))
                
        elif "method" in message:
            # Server request or notification
            # Handle server-initiated requests here if needed
            pass
    
    async def shutdown(self):
        """Shutdown the LSP server."""
        if self.initialized:
            await self.send_request("shutdown")
            await self.send_notification("exit")
            
        if self.process and self.process.returncode is None:
            self.process.terminate()
            await self.process.wait()


class LSPTool(BaseTool):
    """Enhanced LSP tool with full protocol support and compilation capabilities."""
    
    name = "lsp"
    description = """Enhanced Language Server Protocol tool with compilation support.
    
    Actions:
    - definition: Go to definition of symbol
    - references: Find all references
    - rename: Rename symbol across codebase
    - diagnostics: Get errors and warnings
    - hover: Get hover information
    - completion: Get code completions
    - compile: Compile source code
    - run: Compile and run code
    - status: Check LSP server status
    
    Supported languages: C, C++, Go, JavaScript, TypeScript, Rust, Zig, Python
    """
    
    def __init__(self):
        super().__init__()
        self.clients: Dict[str, LSPClient] = {}
        self.logger = logging.getLogger(__name__)
        
    def _detect_language(self, file_path: str) -> Optional[str]:
        """Detect language from file extension."""
        ext = Path(file_path).suffix.lower()
        
        for lang, config in ENHANCED_LSP_SERVERS.items():
            if ext in config["file_extensions"]:
                return lang
                
        return None
    
    def _find_project_root(self, file_path: str, language: str) -> str:
        """Find project root based on markers."""
        markers = ENHANCED_LSP_SERVERS[language]["root_markers"]
        path = Path(file_path).resolve()
        
        for parent in path.parents:
            for marker in markers:
                if (parent / marker).exists():
                    return str(parent)
                    
        return str(path.parent)
    
    async def _get_client(self, language: str, root_uri: str) -> Optional[LSPClient]:
        """Get or create LSP client."""
        key = f"{language}:{root_uri}"
        
        if key not in self.clients:
            client = LSPClient(language, root_uri)
            if await client.start():
                self.clients[key] = client
            else:
                return None
                
        return self.clients[key]
    
    async def _compile_code(self, file_path: str, language: str) -> Dict[str, Any]:
        """Compile source code."""
        config = ENHANCED_LSP_SERVERS[language]
        
        if "compile_cmd" not in config:
            return {"error": f"Compilation not supported for {language}"}
        
        # Prepare compile command
        input_file = Path(file_path)
        output_file = input_file.stem
        
        compile_cmd = [
            part.replace("{input}", str(input_file)).replace("{output}", output_file)
            for part in config["compile_cmd"]
        ]
        
        try:
            # Run compilation
            result = await asyncio.create_subprocess_exec(
                *compile_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=input_file.parent,
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output_file": output_file,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode(),
                    "stdout": stdout.decode(),
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _run_code(self, file_path: str, language: str) -> Dict[str, Any]:
        """Compile and run code."""
        config = ENHANCED_LSP_SERVERS[language]
        
        # Compile if needed
        if "compile_cmd" in config:
            compile_result = await self._compile_code(file_path, language)
            if not compile_result.get("success"):
                return compile_result
                
            run_file = compile_result["output_file"]
        else:
            run_file = file_path
        
        # Run the code
        run_cmd = [
            part.replace("{input}", run_file).replace("{output}", run_file)
            for part in config["run_cmd"]
        ]
        
        try:
            result = await asyncio.create_subprocess_exec(
                *run_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path(file_path).parent,
            )
            
            stdout, stderr = await result.communicate()
            
            return {
                "success": result.returncode == 0,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "exit_code": result.returncode,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def run(
        self,
        action: str,
        file: str,
        line: Optional[int] = None,
        character: Optional[int] = None,
        new_name: Optional[str] = None,
        **kwargs,
    ) -> MCPResourceDocument:
        """Execute LSP action."""
        
        # Detect language
        language = self._detect_language(file)
        if not language:
            return MCPResourceDocument(
                data={
                    "error": f"Unsupported file type: {file}",
                    "supported_languages": list(ENHANCED_LSP_SERVERS.keys()),
                }
            )
        
        # Handle compile and run actions
        if action == "compile":
            result = await self._compile_code(file, language)
            return MCPResourceDocument(data=result)
            
        elif action == "run":
            result = await self._run_code(file, language)
            return MCPResourceDocument(data=result)
        
        # Get LSP client
        root_uri = self._find_project_root(file, language)
        client = await self._get_client(language, root_uri)
        
        if not client:
            return MCPResourceDocument(
                data={"error": f"Failed to start LSP server for {language}"}
            )
        
        # Open the file
        file_uri = f"file://{Path(file).resolve()}"
        with open(file, "r") as f:
            content = f.read()
            
        await client.send_notification(
            "textDocument/didOpen",
            {
                "textDocument": {
                    "uri": file_uri,
                    "languageId": language,
                    "version": 1,
                    "text": content,
                }
            },
        )
        
        # Execute LSP action
        if action == "definition":
            result = await client.send_request(
                "textDocument/definition",
                {
                    "textDocument": {"uri": file_uri},
                    "position": {"line": line - 1, "character": character},
                },
            )
            
        elif action == "references":
            result = await client.send_request(
                "textDocument/references",
                {
                    "textDocument": {"uri": file_uri},
                    "position": {"line": line - 1, "character": character},
                    "context": {"includeDeclaration": True},
                },
            )
            
        elif action == "rename":
            result = await client.send_request(
                "textDocument/rename",
                {
                    "textDocument": {"uri": file_uri},
                    "position": {"line": line - 1, "character": character},
                    "newName": new_name,
                },
            )
            
        elif action == "diagnostics":
            result = await client.send_request(
                "textDocument/diagnostic",
                {
                    "textDocument": {"uri": file_uri},
                },
            )
            
        elif action == "hover":
            result = await client.send_request(
                "textDocument/hover",
                {
                    "textDocument": {"uri": file_uri},
                    "position": {"line": line - 1, "character": character},
                },
            )
            
        elif action == "completion":
            result = await client.send_request(
                "textDocument/completion",
                {
                    "textDocument": {"uri": file_uri},
                    "position": {"line": line - 1, "character": character},
                },
            )
            
        else:
            result = {"error": f"Unknown action: {action}"}
        
        # Close the file
        await client.send_notification(
            "textDocument/didClose",
            {"textDocument": {"uri": file_uri}},
        )
        
        return MCPResourceDocument(data=result)
    
    async def call(self, **kwargs) -> str:
        """Tool interface for MCP."""
        result = await self.run(**kwargs)
        return result.to_json_string()
    
    async def cleanup(self):
        """Clean up all LSP clients."""
        for client in self.clients.values():
            await client.shutdown()


# Factory function
def create_lsp_tool():
    """Create enhanced LSP tool."""
    return LSPTool()