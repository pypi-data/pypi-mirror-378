"""Environment detection tool for automatic development environment configuration.

This tool automatically detects installed development tools, frameworks, and
languages in the user's environment and dynamically loads appropriate MCP tools.
"""

import os
import sys
import json
import shutil
import subprocess
import logging
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass, field

from hanzo_mcp.types import MCPResourceDocument
from hanzo_mcp.tools.common.base import BaseTool


@dataclass
class ToolDetection:
    """Represents a detected development tool."""
    name: str
    version: Optional[str]
    path: str
    category: str  # language, framework, database, etc.
    mcp_tools: List[str] = field(default_factory=list)  # Related MCP tools to enable
    environment: Dict[str, str] = field(default_factory=dict)  # Environment variables


# Tool detection configurations
TOOL_DETECTIONS = {
    # Programming Languages
    "python": {
        "check_cmd": ["python", "--version"],
        "category": "language",
        "mcp_tools": ["run_command", "uvx", "uvx_background"],
        "parse_version": lambda out: out.split()[1] if out else None,
        "frameworks": {
            "django": {
                "check": ["python", "-c", "import django; print(django.get_version())"],
                "mcp_tools": ["django_manage", "django_shell"],
            },
            "fastapi": {
                "check": ["python", "-c", "import fastapi; print(fastapi.__version__)"],
                "mcp_tools": ["uvicorn", "fastapi_routes"],
            },
            "flask": {
                "check": ["python", "-c", "import flask; print(flask.__version__)"],
                "mcp_tools": ["flask_run"],
            },
        },
    },
    "node": {
        "check_cmd": ["node", "--version"],
        "category": "language",
        "mcp_tools": ["npx", "npx_background"],
        "parse_version": lambda out: out.strip().lstrip("v") if out else None,
        "frameworks": {
            "next": {
                "check": ["npm", "list", "next", "--json"],
                "mcp_tools": ["next_dev", "next_build"],
            },
            "react": {
                "check": ["npm", "list", "react", "--json"],
                "mcp_tools": ["react_dev"],
            },
            "vue": {
                "check": ["npm", "list", "vue", "--json"],
                "mcp_tools": ["vue_serve"],
            },
            "angular": {
                "check": ["ng", "version"],
                "mcp_tools": ["ng_serve", "ng_build"],
            },
        },
    },
    "go": {
        "check_cmd": ["go", "version"],
        "category": "language",
        "mcp_tools": ["go_build", "go_run", "go_test"],
        "parse_version": lambda out: out.split()[2].lstrip("go") if out else None,
        "frameworks": {
            "gin": {
                "check_file": "go.mod",
                "check_content": "github.com/gin-gonic/gin",
                "mcp_tools": ["gin_server"],
            },
            "echo": {
                "check_file": "go.mod",
                "check_content": "github.com/labstack/echo",
                "mcp_tools": ["echo_server"],
            },
        },
    },
    "rust": {
        "check_cmd": ["rustc", "--version"],
        "category": "language",
        "mcp_tools": ["cargo_build", "cargo_run", "cargo_test"],
        "parse_version": lambda out: out.split()[1] if out else None,
        "frameworks": {
            "actix": {
                "check_file": "Cargo.toml",
                "check_content": 'actix-web',
                "mcp_tools": ["actix_server"],
            },
            "rocket": {
                "check_file": "Cargo.toml",
                "check_content": 'rocket',
                "mcp_tools": ["rocket_server"],
            },
        },
    },
    "java": {
        "check_cmd": ["java", "--version"],
        "category": "language",
        "mcp_tools": ["javac", "java_run"],
        "parse_version": lambda out: out.split()[1] if out else None,
        "frameworks": {
            "spring": {
                "check_file": "pom.xml",
                "check_content": "spring-boot",
                "mcp_tools": ["spring_boot", "mvn"],
            },
        },
    },
    "cpp": {
        "check_cmd": ["clang++", "--version"],
        "category": "language",
        "mcp_tools": ["cmake", "make", "clang_compile"],
        "parse_version": lambda out: out.split()[2] if "version" in out else None,
    },
    "c": {
        "check_cmd": ["clang", "--version"],
        "category": "language",
        "mcp_tools": ["cmake", "make", "clang_compile"],
        "parse_version": lambda out: out.split()[2] if "version" in out else None,
    },
    "zig": {
        "check_cmd": ["zig", "version"],
        "category": "language",
        "mcp_tools": ["zig_build", "zig_run", "zig_test"],
        "parse_version": lambda out: out.strip() if out else None,
    },
    # Databases
    "postgresql": {
        "check_cmd": ["psql", "--version"],
        "category": "database",
        "mcp_tools": ["sql_query", "sql_search", "sql_stats"],
        "parse_version": lambda out: out.split()[-1] if out else None,
    },
    "mysql": {
        "check_cmd": ["mysql", "--version"],
        "category": "database",
        "mcp_tools": ["sql_query", "sql_search", "sql_stats"],
        "parse_version": lambda out: out.split()[4].rstrip(",") if out else None,
    },
    "redis": {
        "check_cmd": ["redis-cli", "--version"],
        "category": "database",
        "mcp_tools": ["redis_get", "redis_set", "redis_keys"],
        "parse_version": lambda out: out.split()[2] if out else None,
    },
    "mongodb": {
        "check_cmd": ["mongod", "--version"],
        "category": "database",
        "mcp_tools": ["mongo_query", "mongo_insert"],
        "parse_version": lambda out: out.split()[2] if "version" in out else None,
    },
    # Container & Orchestration
    "docker": {
        "check_cmd": ["docker", "--version"],
        "category": "container",
        "mcp_tools": ["docker_build", "docker_run", "docker_ps"],
        "parse_version": lambda out: out.split()[2].rstrip(",") if out else None,
    },
    "kubernetes": {
        "check_cmd": ["kubectl", "version", "--client", "--short"],
        "category": "orchestration",
        "mcp_tools": ["kubectl_apply", "kubectl_get", "kubectl_logs"],
        "parse_version": lambda out: out.split()[-1] if out else None,
    },
    # Version Control
    "git": {
        "check_cmd": ["git", "--version"],
        "category": "vcs",
        "mcp_tools": ["git_search", "git_log", "git_diff"],
        "parse_version": lambda out: out.split()[-1] if out else None,
    },
    # Package Managers
    "npm": {
        "check_cmd": ["npm", "--version"],
        "category": "package_manager",
        "mcp_tools": ["npx", "npm_install"],
        "parse_version": lambda out: out.strip() if out else None,
    },
    "yarn": {
        "check_cmd": ["yarn", "--version"],
        "category": "package_manager",
        "mcp_tools": ["yarn_install", "yarn_run"],
        "parse_version": lambda out: out.strip() if out else None,
    },
    "pnpm": {
        "check_cmd": ["pnpm", "--version"],
        "category": "package_manager",
        "mcp_tools": ["pnpm_install", "pnpm_run"],
        "parse_version": lambda out: out.strip() if out else None,
    },
    "pip": {
        "check_cmd": ["pip", "--version"],
        "category": "package_manager",
        "mcp_tools": ["pip_install", "pip_freeze"],
        "parse_version": lambda out: out.split()[1] if out else None,
    },
    "cargo": {
        "check_cmd": ["cargo", "--version"],
        "category": "package_manager",
        "mcp_tools": ["cargo_build", "cargo_run"],
        "parse_version": lambda out: out.split()[1] if out else None,
    },
    # Build Tools
    "make": {
        "check_cmd": ["make", "--version"],
        "category": "build",
        "mcp_tools": ["make_build", "make_clean"],
        "parse_version": lambda out: out.split()[-1] if out else None,
    },
    "cmake": {
        "check_cmd": ["cmake", "--version"],
        "category": "build",
        "mcp_tools": ["cmake_configure", "cmake_build"],
        "parse_version": lambda out: out.split()[2] if out else None,
    },
}


class EnvironmentDetector(BaseTool):
    """Tool for detecting and configuring development environment."""
    
    name = "env_detect"
    description = """Detect development environment and auto-configure tools.
    
    Actions:
    - detect: Detect all installed development tools
    - check: Check specific tool availability
    - suggest: Suggest tools to install for project
    - configure: Auto-configure MCP tools based on detection
    - export: Export environment configuration
    
    This tool helps automatically configure your development environment
    by detecting installed languages, frameworks, databases, and tools.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.detected_tools: List[ToolDetection] = []
        self.project_root = self._find_project_root()
        
    def _find_project_root(self) -> Path:
        """Find project root directory."""
        markers = [
            ".git", "package.json", "pyproject.toml", "Cargo.toml",
            "go.mod", "pom.xml", "build.gradle", "CMakeLists.txt"
        ]
        
        cwd = Path.cwd()
        for parent in [cwd] + list(cwd.parents):
            for marker in markers:
                if (parent / marker).exists():
                    return parent
                    
        return cwd
    
    def _run_command(self, cmd: List[str]) -> Optional[str]:
        """Run command and return output."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
            
        return None
    
    def _check_file_content(self, file_path: str, content: str) -> bool:
        """Check if file contains specific content."""
        try:
            file = self.project_root / file_path
            if file.exists():
                with open(file, "r") as f:
                    return content in f.read()
        except Exception:
            pass
            
        return False
    
    def _detect_tool(self, tool_name: str, config: Dict[str, Any]) -> Optional[ToolDetection]:
        """Detect a specific tool."""
        # Check main tool
        output = self._run_command(config["check_cmd"])
        if not output:
            return None
            
        # Parse version
        version = None
        if "parse_version" in config:
            try:
                version = config["parse_version"](output)
            except Exception:
                pass
        
        # Find executable path
        executable = config["check_cmd"][0]
        path = shutil.which(executable) or executable
        
        # Create detection
        detection = ToolDetection(
            name=tool_name,
            version=version,
            path=path,
            category=config["category"],
            mcp_tools=config.get("mcp_tools", []),
        )
        
        # Check frameworks if applicable
        if "frameworks" in config:
            for fw_name, fw_config in config["frameworks"].items():
                if self._check_framework(fw_config):
                    detection.mcp_tools.extend(fw_config.get("mcp_tools", []))
                    self.logger.info(f"Detected {fw_name} framework")
        
        return detection
    
    def _check_framework(self, config: Dict[str, Any]) -> bool:
        """Check if framework is present."""
        if "check" in config:
            output = self._run_command(config["check"])
            return output is not None
            
        if "check_file" in config and "check_content" in config:
            return self._check_file_content(config["check_file"], config["check_content"])
            
        return False
    
    def detect_all(self) -> List[ToolDetection]:
        """Detect all available tools."""
        self.detected_tools = []
        
        for tool_name, config in TOOL_DETECTIONS.items():
            detection = self._detect_tool(tool_name, config)
            if detection:
                self.detected_tools.append(detection)
                self.logger.info(f"Detected {tool_name} v{detection.version}")
        
        return self.detected_tools
    
    def suggest_tools(self) -> Dict[str, List[str]]:
        """Suggest tools to install based on project."""
        suggestions = {
            "languages": [],
            "frameworks": [],
            "tools": [],
        }
        
        # Check project files
        files = list(self.project_root.glob("*"))
        file_names = [f.name for f in files]
        
        # Language suggestions
        if "package.json" in file_names and "node" not in [d.name for d in self.detected_tools]:
            suggestions["languages"].append("node")
            
        if "requirements.txt" in file_names and "python" not in [d.name for d in self.detected_tools]:
            suggestions["languages"].append("python")
            
        if "Cargo.toml" in file_names and "rust" not in [d.name for d in self.detected_tools]:
            suggestions["languages"].append("rust")
            
        if "go.mod" in file_names and "go" not in [d.name for d in self.detected_tools]:
            suggestions["languages"].append("go")
        
        # Tool suggestions
        if any(d.category == "language" for d in self.detected_tools):
            if "git" not in [d.name for d in self.detected_tools]:
                suggestions["tools"].append("git")
                
            if "docker" not in [d.name for d in self.detected_tools]:
                suggestions["tools"].append("docker")
        
        return suggestions
    
    def get_enabled_mcp_tools(self) -> Set[str]:
        """Get list of MCP tools to enable based on detection."""
        tools = set()
        
        for detection in self.detected_tools:
            tools.update(detection.mcp_tools)
        
        # Always include essential tools
        essential = [
            "read", "write", "edit", "multi_edit",
            "directory_tree", "grep", "find", "search",
            "run_command", "bash", "ast", "lsp"
        ]
        tools.update(essential)
        
        return tools
    
    def generate_configuration(self) -> Dict[str, Any]:
        """Generate MCP configuration based on detection."""
        config = {
            "detected_environment": {
                "project_root": str(self.project_root),
                "tools": [
                    {
                        "name": d.name,
                        "version": d.version,
                        "category": d.category,
                        "path": d.path,
                    }
                    for d in self.detected_tools
                ],
            },
            "enabled_mcp_tools": sorted(self.get_enabled_mcp_tools()),
            "environment_variables": {},
            "modes": [],
        }
        
        # Add environment variables
        for detection in self.detected_tools:
            config["environment_variables"].update(detection.environment)
        
        # Determine modes to enable
        categories = {d.category for d in self.detected_tools}
        languages = {d.name for d in self.detected_tools if d.category == "language"}
        
        if "python" in languages:
            config["modes"].append("python")
            if any("django" in t for d in self.detected_tools for t in d.mcp_tools):
                config["modes"].append("django")
            if any("fastapi" in t for d in self.detected_tools for t in d.mcp_tools):
                config["modes"].append("fastapi")
                
        if "node" in languages or "typescript" in languages:
            config["modes"].append("javascript")
            if any("next" in t for d in self.detected_tools for t in d.mcp_tools):
                config["modes"].append("nextjs")
            if any("react" in t for d in self.detected_tools for t in d.mcp_tools):
                config["modes"].append("react")
                
        if "rust" in languages:
            config["modes"].append("rust")
            
        if "go" in languages:
            config["modes"].append("go")
        
        return config
    
    async def run(
        self,
        action: str = "detect",
        tool: Optional[str] = None,
        export_path: Optional[str] = None,
        **kwargs,
    ) -> MCPResourceDocument:
        """Execute environment detection action."""
        
        if action == "detect":
            # Detect all tools
            detections = self.detect_all()
            
            return MCPResourceDocument(
                data={
                    "detected_tools": [
                        {
                            "name": d.name,
                            "version": d.version,
                            "category": d.category,
                            "path": d.path,
                            "mcp_tools": d.mcp_tools,
                        }
                        for d in detections
                    ],
                    "total": len(detections),
                    "categories": list(set(d.category for d in detections)),
                }
            )
            
        elif action == "check":
            # Check specific tool
            if not tool:
                return MCPResourceDocument(data={"error": "Tool name required for check action"})
                
            if tool in TOOL_DETECTIONS:
                detection = self._detect_tool(tool, TOOL_DETECTIONS[tool])
                if detection:
                    return MCPResourceDocument(
                        data={
                            "available": True,
                            "name": detection.name,
                            "version": detection.version,
                            "path": detection.path,
                            "mcp_tools": detection.mcp_tools,
                        }
                    )
                else:
                    return MCPResourceDocument(
                        data={
                            "available": False,
                            "name": tool,
                            "install_hint": f"Install {tool} to enable related MCP tools",
                        }
                    )
            else:
                return MCPResourceDocument(data={"error": f"Unknown tool: {tool}"})
                
        elif action == "suggest":
            # Suggest tools to install
            if not self.detected_tools:
                self.detect_all()
                
            suggestions = self.suggest_tools()
            
            return MCPResourceDocument(
                data={
                    "suggestions": suggestions,
                    "detected": [d.name for d in self.detected_tools],
                }
            )
            
        elif action == "configure":
            # Generate and apply configuration
            if not self.detected_tools:
                self.detect_all()
                
            config = self.generate_configuration()
            
            # Save configuration if export path provided
            if export_path:
                export_file = Path(export_path)
                export_file.write_text(json.dumps(config, indent=2))
                config["exported_to"] = str(export_file)
            
            return MCPResourceDocument(data=config)
            
        elif action == "export":
            # Export configuration
            if not self.detected_tools:
                self.detect_all()
                
            config = self.generate_configuration()
            
            if export_path:
                export_file = Path(export_path)
                export_file.write_text(json.dumps(config, indent=2))
                
                return MCPResourceDocument(
                    data={
                        "exported": True,
                        "path": str(export_file),
                        "configuration": config,
                    }
                )
            else:
                return MCPResourceDocument(data=config)
                
        else:
            return MCPResourceDocument(
                data={
                    "error": f"Unknown action: {action}",
                    "valid_actions": ["detect", "check", "suggest", "configure", "export"],
                }
            )
    
    async def call(self, **kwargs) -> str:
        """Tool interface for MCP."""
        result = await self.run(**kwargs)
        return result.to_json_string()


# Factory function
def create_environment_detector():
    """Create environment detection tool."""
    return EnvironmentDetector()