"""Framework-specific modes for dynamic tool loading.

This module provides mode management for different development frameworks,
allowing dynamic loading of framework-specific tools and configurations.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from pathlib import Path

from hanzo_mcp.types import MCPResourceDocument
from hanzo_mcp.tools.common.base import BaseTool


@dataclass
class FrameworkMode:
    """Represents a framework-specific mode."""
    name: str
    description: str
    category: str  # language, web, mobile, data, etc.
    tools: List[str]  # MCP tools to enable
    aliases: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    snippets: Dict[str, str] = field(default_factory=dict)  # Code snippets
    commands: Dict[str, List[str]] = field(default_factory=dict)  # Common commands
    dependencies: List[str] = field(default_factory=list)  # Required modes


# Framework mode definitions
FRAMEWORK_MODES = {
    # Python Frameworks
    "django": FrameworkMode(
        name="django",
        description="Django web framework mode",
        category="web",
        tools=[
            "run_command", "python", "pip_install",
            "django_manage", "django_shell", "django_migrate",
            "django_makemigrations", "django_test", "django_runserver"
        ],
        aliases=["dj"],
        environment={
            "DJANGO_SETTINGS_MODULE": "settings",
            "PYTHONPATH": ".",
        },
        snippets={
            "model": """from django.db import models

class {ModelName}(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']""",
            "view": """from django.shortcuts import render
from django.views import View

class {ViewName}(View):
    def get(self, request):
        return render(request, 'template.html', {})""",
        },
        commands={
            "serve": ["python", "manage.py", "runserver"],
            "migrate": ["python", "manage.py", "migrate"],
            "test": ["python", "manage.py", "test"],
        },
        dependencies=["python"],
    ),
    
    "fastapi": FrameworkMode(
        name="fastapi",
        description="FastAPI web framework mode",
        category="web",
        tools=[
            "run_command", "python", "uvicorn",
            "fastapi_routes", "fastapi_swagger", "fastapi_test"
        ],
        aliases=["fa"],
        environment={
            "PYTHONPATH": ".",
        },
        snippets={
            "endpoint": """from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class {ModelName}(BaseModel):
    field: str

@app.post("/{endpoint}")
async def {function_name}(data: {ModelName}):
    return {"message": "success", "data": data}""",
        },
        commands={
            "serve": ["uvicorn", "main:app", "--reload"],
            "test": ["pytest", "-v"],
        },
        dependencies=["python"],
    ),
    
    "flask": FrameworkMode(
        name="flask",
        description="Flask web framework mode",
        category="web",
        tools=[
            "run_command", "python", "flask_run",
            "flask_shell", "flask_routes"
        ],
        aliases=["fl"],
        environment={
            "FLASK_APP": "app.py",
            "FLASK_ENV": "development",
        },
        snippets={
            "route": """from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/{endpoint}', methods=['GET', 'POST'])
def {function_name}():
    if request.method == 'POST':
        data = request.json
        return jsonify({"message": "success", "data": data})
    return jsonify({"message": "GET request"})""",
        },
        commands={
            "serve": ["flask", "run"],
            "shell": ["flask", "shell"],
        },
        dependencies=["python"],
    ),
    
    # JavaScript/TypeScript Frameworks
    "nextjs": FrameworkMode(
        name="nextjs",
        description="Next.js React framework mode",
        category="web",
        tools=[
            "npx", "npm_install", "next_dev", "next_build",
            "next_start", "next_lint", "react_component"
        ],
        aliases=["next"],
        environment={
            "NODE_ENV": "development",
        },
        snippets={
            "page": """export default function {PageName}() {
  return (
    <div>
      <h1>{PageName}</h1>
    </div>
  );
}""",
            "api": """export default function handler(req, res) {
  if (req.method === 'POST') {
    const data = req.body;
    res.status(200).json({ message: 'Success', data });
  } else {
    res.status(200).json({ message: 'GET request' });
  }
}""",
        },
        commands={
            "dev": ["npm", "run", "dev"],
            "build": ["npm", "run", "build"],
            "start": ["npm", "run", "start"],
        },
        dependencies=["javascript", "react"],
    ),
    
    "react": FrameworkMode(
        name="react",
        description="React framework mode",
        category="web",
        tools=[
            "npx", "npm_install", "react_component",
            "react_hook", "react_context"
        ],
        aliases=["r"],
        snippets={
            "component": """import React from 'react';

export const {ComponentName} = () => {
  return (
    <div>
      <h1>{ComponentName}</h1>
    </div>
  );
};""",
            "hook": """import { useState, useEffect } from 'react';

export const use{HookName} = () => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    // Effect logic
  }, []);
  
  return { data };
};""",
        },
        commands={
            "start": ["npm", "start"],
            "build": ["npm", "run", "build"],
            "test": ["npm", "test"],
        },
        dependencies=["javascript"],
    ),
    
    "vue": FrameworkMode(
        name="vue",
        description="Vue.js framework mode",
        category="web",
        tools=[
            "npx", "npm_install", "vue_component",
            "vue_store", "vue_router"
        ],
        aliases=["v"],
        snippets={
            "component": """<template>
  <div>
    <h1>{{ title }}</h1>
  </div>
</template>

<script>
export default {
  name: '{ComponentName}',
  data() {
    return {
      title: '{ComponentName}'
    };
  }
};
</script>""",
        },
        commands={
            "serve": ["npm", "run", "serve"],
            "build": ["npm", "run", "build"],
        },
        dependencies=["javascript"],
    ),
    
    # Rust Frameworks
    "actix": FrameworkMode(
        name="actix",
        description="Actix web framework mode",
        category="web",
        tools=[
            "cargo_build", "cargo_run", "cargo_test",
            "actix_handler", "actix_middleware"
        ],
        aliases=["ax"],
        snippets={
            "handler": """use actix_web::{web, HttpResponse, Result};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct {ModelName} {
    field: String,
}

pub async fn {handler_name}(data: web::Json<{ModelName}>) -> Result<HttpResponse> {
    Ok(HttpResponse::Ok().json(&data.into_inner()))
}""",
        },
        commands={
            "run": ["cargo", "run"],
            "build": ["cargo", "build", "--release"],
            "test": ["cargo", "test"],
        },
        dependencies=["rust"],
    ),
    
    # Go Frameworks
    "gin": FrameworkMode(
        name="gin",
        description="Gin web framework mode",
        category="web",
        tools=[
            "go_build", "go_run", "go_test",
            "gin_handler", "gin_middleware"
        ],
        aliases=["g"],
        snippets={
            "handler": """func {HandlerName}(c *gin.Context) {
    var data struct {
        Field string `json:"field"`
    }
    
    if err := c.ShouldBindJSON(&data); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
    
    c.JSON(200, gin.H{
        "message": "success",
        "data": data,
    })
}""",
        },
        commands={
            "run": ["go", "run", "."],
            "build": ["go", "build"],
            "test": ["go", "test", "./..."],
        },
        dependencies=["go"],
    ),
    
    # Language Modes (Base modes)
    "python": FrameworkMode(
        name="python",
        description="Python language mode",
        category="language",
        tools=[
            "run_command", "python", "pip", "pytest",
            "black", "ruff", "mypy", "uvx"
        ],
        environment={
            "PYTHONPATH": ".",
        },
        commands={
            "run": ["python"],
            "test": ["pytest"],
            "format": ["black", "."],
            "lint": ["ruff", "check", "."],
        },
    ),
    
    "javascript": FrameworkMode(
        name="javascript",
        description="JavaScript/TypeScript language mode",
        category="language",
        tools=[
            "npx", "npm", "node", "tsc",
            "eslint", "prettier", "jest"
        ],
        commands={
            "run": ["node"],
            "test": ["npm", "test"],
            "format": ["prettier", "--write", "."],
            "lint": ["eslint", "."],
        },
    ),
    
    "rust": FrameworkMode(
        name="rust",
        description="Rust language mode",
        category="language",
        tools=[
            "cargo", "rustc", "rustfmt", "clippy"
        ],
        commands={
            "build": ["cargo", "build"],
            "run": ["cargo", "run"],
            "test": ["cargo", "test"],
            "format": ["cargo", "fmt"],
            "lint": ["cargo", "clippy"],
        },
    ),
    
    "go": FrameworkMode(
        name="go",
        description="Go language mode",
        category="language",
        tools=[
            "go", "gofmt", "golint", "gotest"
        ],
        commands={
            "build": ["go", "build"],
            "run": ["go", "run", "."],
            "test": ["go", "test", "./..."],
            "format": ["go", "fmt", "./..."],
        },
    ),
}


class FrameworkModeManager(BaseTool):
    """Manager for framework-specific modes."""
    
    name = "framework_mode"
    description = """Manage framework-specific development modes.
    
    Actions:
    - enable: Enable a framework mode
    - disable: Disable a framework mode
    - list: List available modes
    - current: Show currently active modes
    - info: Get information about a mode
    - snippet: Get code snippet for framework
    - command: Get command for framework task
    
    Modes automatically load framework-specific tools and configurations.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.active_modes: Set[str] = set()
        self.mode_stack: List[str] = []  # For mode history
        
    def _resolve_dependencies(self, mode_name: str) -> List[str]:
        """Resolve mode dependencies."""
        if mode_name not in FRAMEWORK_MODES:
            return []
            
        mode = FRAMEWORK_MODES[mode_name]
        dependencies = []
        
        # Add dependencies recursively
        for dep in mode.dependencies:
            dependencies.extend(self._resolve_dependencies(dep))
            dependencies.append(dep)
            
        return dependencies
    
    def enable_mode(self, mode_name: str) -> Dict[str, Any]:
        """Enable a framework mode."""
        # Check if mode exists
        if mode_name not in FRAMEWORK_MODES:
            # Check aliases
            for name, mode in FRAMEWORK_MODES.items():
                if mode_name in mode.aliases:
                    mode_name = name
                    break
            else:
                return {
                    "success": False,
                    "error": f"Unknown mode: {mode_name}",
                    "available_modes": list(FRAMEWORK_MODES.keys()),
                }
        
        mode = FRAMEWORK_MODES[mode_name]
        
        # Resolve dependencies
        dependencies = self._resolve_dependencies(mode_name)
        
        # Enable dependencies first
        for dep in dependencies:
            if dep not in self.active_modes:
                self.active_modes.add(dep)
                self.logger.info(f"Enabled dependency mode: {dep}")
        
        # Enable the mode
        self.active_modes.add(mode_name)
        self.mode_stack.append(mode_name)
        
        # Get all tools to enable
        tools = set(mode.tools)
        for dep in dependencies:
            tools.update(FRAMEWORK_MODES[dep].tools)
        
        return {
            "success": True,
            "mode": mode_name,
            "description": mode.description,
            "category": mode.category,
            "enabled_tools": sorted(tools),
            "dependencies_enabled": dependencies,
            "environment": mode.environment,
            "active_modes": sorted(self.active_modes),
        }
    
    def disable_mode(self, mode_name: str) -> Dict[str, Any]:
        """Disable a framework mode."""
        if mode_name not in self.active_modes:
            return {
                "success": False,
                "error": f"Mode not active: {mode_name}",
                "active_modes": sorted(self.active_modes),
            }
        
        # Remove from active modes
        self.active_modes.discard(mode_name)
        
        # Remove from stack
        if mode_name in self.mode_stack:
            self.mode_stack.remove(mode_name)
        
        # Check if any active modes depend on this
        dependent_modes = []
        for active in self.active_modes.copy():
            mode = FRAMEWORK_MODES[active]
            if mode_name in mode.dependencies:
                dependent_modes.append(active)
                self.active_modes.discard(active)
        
        return {
            "success": True,
            "mode": mode_name,
            "disabled": True,
            "dependent_modes_disabled": dependent_modes,
            "active_modes": sorted(self.active_modes),
        }
    
    def get_snippet(self, mode_name: str, snippet_name: str) -> Optional[str]:
        """Get code snippet for framework."""
        if mode_name not in FRAMEWORK_MODES:
            return None
            
        mode = FRAMEWORK_MODES[mode_name]
        return mode.snippets.get(snippet_name)
    
    def get_command(self, mode_name: str, command_name: str) -> Optional[List[str]]:
        """Get command for framework task."""
        if mode_name not in FRAMEWORK_MODES:
            return None
            
        mode = FRAMEWORK_MODES[mode_name]
        return mode.commands.get(command_name)
    
    def list_modes(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available modes."""
        modes = []
        
        for name, mode in FRAMEWORK_MODES.items():
            if category and mode.category != category:
                continue
                
            modes.append({
                "name": name,
                "description": mode.description,
                "category": mode.category,
                "aliases": mode.aliases,
                "active": name in self.active_modes,
                "tools_count": len(mode.tools),
                "has_snippets": bool(mode.snippets),
                "has_commands": bool(mode.commands),
            })
        
        return modes
    
    def get_mode_info(self, mode_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a mode."""
        if mode_name not in FRAMEWORK_MODES:
            return None
            
        mode = FRAMEWORK_MODES[mode_name]
        
        return {
            "name": mode.name,
            "description": mode.description,
            "category": mode.category,
            "aliases": mode.aliases,
            "active": mode.name in self.active_modes,
            "tools": mode.tools,
            "environment": mode.environment,
            "snippets": list(mode.snippets.keys()),
            "commands": list(mode.commands.keys()),
            "dependencies": mode.dependencies,
        }
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export current mode configuration."""
        config = {
            "active_modes": sorted(self.active_modes),
            "mode_stack": self.mode_stack,
            "enabled_tools": set(),
            "environment": {},
            "commands": {},
        }
        
        # Collect all enabled tools and environment
        for mode_name in self.active_modes:
            mode = FRAMEWORK_MODES[mode_name]
            config["enabled_tools"].update(mode.tools)
            config["environment"].update(mode.environment)
            
            # Add commands with mode prefix
            for cmd_name, cmd in mode.commands.items():
                config["commands"][f"{mode_name}:{cmd_name}"] = cmd
        
        config["enabled_tools"] = sorted(config["enabled_tools"])
        
        return config
    
    async def run(
        self,
        action: str,
        mode: Optional[str] = None,
        snippet: Optional[str] = None,
        command: Optional[str] = None,
        category: Optional[str] = None,
        **kwargs,
    ) -> MCPResourceDocument:
        """Execute framework mode action."""
        
        if action == "enable":
            if not mode:
                return MCPResourceDocument(data={"error": "Mode name required"})
                
            result = self.enable_mode(mode)
            return MCPResourceDocument(data=result)
            
        elif action == "disable":
            if not mode:
                return MCPResourceDocument(data={"error": "Mode name required"})
                
            result = self.disable_mode(mode)
            return MCPResourceDocument(data=result)
            
        elif action == "list":
            modes = self.list_modes(category)
            
            return MCPResourceDocument(
                data={
                    "modes": modes,
                    "total": len(modes),
                    "active_count": len(self.active_modes),
                    "categories": list(set(m["category"] for m in modes)),
                }
            )
            
        elif action == "current":
            config = self.export_configuration()
            
            return MCPResourceDocument(data=config)
            
        elif action == "info":
            if not mode:
                return MCPResourceDocument(data={"error": "Mode name required"})
                
            info = self.get_mode_info(mode)
            
            if info:
                return MCPResourceDocument(data=info)
            else:
                return MCPResourceDocument(
                    data={
                        "error": f"Unknown mode: {mode}",
                        "available_modes": list(FRAMEWORK_MODES.keys()),
                    }
                )
                
        elif action == "snippet":
            if not mode or not snippet:
                return MCPResourceDocument(
                    data={"error": "Mode and snippet name required"}
                )
                
            code = self.get_snippet(mode, snippet)
            
            if code:
                return MCPResourceDocument(
                    data={
                        "mode": mode,
                        "snippet": snippet,
                        "code": code,
                    }
                )
            else:
                mode_obj = FRAMEWORK_MODES.get(mode)
                available = list(mode_obj.snippets.keys()) if mode_obj else []
                
                return MCPResourceDocument(
                    data={
                        "error": f"Snippet '{snippet}' not found for mode '{mode}'",
                        "available_snippets": available,
                    }
                )
                
        elif action == "command":
            if not mode or not command:
                return MCPResourceDocument(
                    data={"error": "Mode and command name required"}
                )
                
            cmd = self.get_command(mode, command)
            
            if cmd:
                return MCPResourceDocument(
                    data={
                        "mode": mode,
                        "command": command,
                        "cmd": cmd,
                        "executable": " ".join(cmd),
                    }
                )
            else:
                mode_obj = FRAMEWORK_MODES.get(mode)
                available = list(mode_obj.commands.keys()) if mode_obj else []
                
                return MCPResourceDocument(
                    data={
                        "error": f"Command '{command}' not found for mode '{mode}'",
                        "available_commands": available,
                    }
                )
                
        else:
            return MCPResourceDocument(
                data={
                    "error": f"Unknown action: {action}",
                    "valid_actions": [
                        "enable", "disable", "list", "current",
                        "info", "snippet", "command"
                    ],
                }
            )
    
    async def call(self, **kwargs) -> str:
        """Tool interface for MCP."""
        result = await self.run(**kwargs)
        return result.to_json_string()


# Factory function
def create_framework_mode_manager():
    """Create framework mode manager."""
    return FrameworkModeManager()