"""Sandboxed multi-language compiler and execution tool.

This tool provides safe compilation and execution of code in multiple
languages with sandboxing, resource limits, and timeout controls.
"""

import os
import sys
import json
import asyncio
import tempfile
import shutil
import logging
import resource
import signal
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from hanzo_mcp.types import MCPResourceDocument
from hanzo_mcp.tools.common.base import BaseTool


class Language(Enum):
    """Supported programming languages."""
    C = "c"
    CPP = "cpp"
    GO = "go"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    RUST = "rust"
    ZIG = "zig"
    PYTHON = "python"
    JAVA = "java"
    KOTLIN = "kotlin"
    SWIFT = "swift"
    RUBY = "ruby"
    PHP = "php"


@dataclass
class CompilerConfig:
    """Compiler configuration for a language."""
    language: Language
    compiler_cmd: List[str]
    run_cmd: List[str]
    file_extension: str
    needs_compilation: bool
    docker_image: Optional[str] = None
    sandbox_cmd: Optional[List[str]] = None


# Language compiler configurations
COMPILER_CONFIGS = {
    Language.C: CompilerConfig(
        language=Language.C,
        compiler_cmd=["clang", "-O2", "-o", "{output}", "{input}"],
        run_cmd=["./{output}"],
        file_extension=".c",
        needs_compilation=True,
        docker_image="gcc:latest",
        sandbox_cmd=["docker", "run", "--rm", "-v", "{mount}:/code", "gcc:latest"],
    ),
    
    Language.CPP: CompilerConfig(
        language=Language.CPP,
        compiler_cmd=["clang++", "-std=c++17", "-O2", "-o", "{output}", "{input}"],
        run_cmd=["./{output}"],
        file_extension=".cpp",
        needs_compilation=True,
        docker_image="gcc:latest",
        sandbox_cmd=["docker", "run", "--rm", "-v", "{mount}:/code", "gcc:latest"],
    ),
    
    Language.GO: CompilerConfig(
        language=Language.GO,
        compiler_cmd=["go", "build", "-o", "{output}", "{input}"],
        run_cmd=["./{output}"],
        file_extension=".go",
        needs_compilation=True,
        docker_image="golang:latest",
        sandbox_cmd=["docker", "run", "--rm", "-v", "{mount}:/code", "golang:latest"],
    ),
    
    Language.JAVASCRIPT: CompilerConfig(
        language=Language.JAVASCRIPT,
        compiler_cmd=[],
        run_cmd=["node", "{input}"],
        file_extension=".js",
        needs_compilation=False,
        docker_image="node:latest",
        sandbox_cmd=["docker", "run", "--rm", "-v", "{mount}:/code", "node:latest"],
    ),
    
    Language.TYPESCRIPT: CompilerConfig(
        language=Language.TYPESCRIPT,
        compiler_cmd=["tsc", "{input}", "--outFile", "{output}.js"],
        run_cmd=["node", "{output}.js"],
        file_extension=".ts",
        needs_compilation=True,
        docker_image="node:latest",
        sandbox_cmd=["docker", "run", "--rm", "-v", "{mount}:/code", "node:latest"],
    ),
    
    Language.RUST: CompilerConfig(
        language=Language.RUST,
        compiler_cmd=["rustc", "-O", "-o", "{output}", "{input}"],
        run_cmd=["./{output}"],
        file_extension=".rs",
        needs_compilation=True,
        docker_image="rust:latest",
        sandbox_cmd=["docker", "run", "--rm", "-v", "{mount}:/code", "rust:latest"],
    ),
    
    Language.ZIG: CompilerConfig(
        language=Language.ZIG,
        compiler_cmd=["zig", "build-exe", "{input}", "-femit-bin={output}"],
        run_cmd=["./{output}"],
        file_extension=".zig",
        needs_compilation=True,
        docker_image="euantorano/zig:latest",
        sandbox_cmd=["docker", "run", "--rm", "-v", "{mount}:/code", "euantorano/zig:latest"],
    ),
    
    Language.PYTHON: CompilerConfig(
        language=Language.PYTHON,
        compiler_cmd=[],
        run_cmd=["python", "{input}"],
        file_extension=".py",
        needs_compilation=False,
        docker_image="python:latest",
        sandbox_cmd=["docker", "run", "--rm", "-v", "{mount}:/code", "python:latest"],
    ),
    
    Language.JAVA: CompilerConfig(
        language=Language.JAVA,
        compiler_cmd=["javac", "{input}"],
        run_cmd=["java", "{classname}"],
        file_extension=".java",
        needs_compilation=True,
        docker_image="openjdk:latest",
        sandbox_cmd=["docker", "run", "--rm", "-v", "{mount}:/code", "openjdk:latest"],
    ),
    
    Language.RUBY: CompilerConfig(
        language=Language.RUBY,
        compiler_cmd=[],
        run_cmd=["ruby", "{input}"],
        file_extension=".rb",
        needs_compilation=False,
        docker_image="ruby:latest",
        sandbox_cmd=["docker", "run", "--rm", "-v", "{mount}:/code", "ruby:latest"],
    ),
}


class SandboxExecutor:
    """Executes code in a sandboxed environment."""
    
    def __init__(self, use_docker: bool = False):
        self.use_docker = use_docker
        self.logger = logging.getLogger(__name__)
        
    async def execute(
        self,
        cmd: List[str],
        cwd: str,
        timeout: int = 10,
        memory_limit: int = 256 * 1024 * 1024,  # 256 MB
        stdin_data: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Execute command with sandboxing."""
        
        if self.use_docker:
            return await self._execute_docker(cmd, cwd, timeout, stdin_data)
        else:
            return await self._execute_native(cmd, cwd, timeout, memory_limit, stdin_data)
    
    async def _execute_native(
        self,
        cmd: List[str],
        cwd: str,
        timeout: int,
        memory_limit: int,
        stdin_data: Optional[str],
    ) -> Tuple[int, str, str]:
        """Execute with native sandboxing."""
        
        # Create process with resource limits
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE if stdin_data else None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                preexec_fn=lambda: self._set_limits(memory_limit) if sys.platform != "win32" else None,
            )
            
            # Send input and get output
            stdout, stderr = await asyncio.wait_for(
                process.communicate(stdin_data.encode() if stdin_data else None),
                timeout=timeout,
            )
            
            return process.returncode, stdout.decode(), stderr.decode()
            
        except asyncio.TimeoutError:
            if process:
                process.kill()
                await process.wait()
            return -1, "", "Execution timed out"
            
        except Exception as e:
            return -1, "", str(e)
    
    def _set_limits(self, memory_limit: int):
        """Set resource limits for process."""
        # Memory limit
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
        
        # CPU time limit (10 seconds)
        resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
        
        # No file creation
        resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
        
        # Limited number of processes
        resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
    
    async def _execute_docker(
        self,
        cmd: List[str],
        cwd: str,
        timeout: int,
        stdin_data: Optional[str],
    ) -> Tuple[int, str, str]:
        """Execute with Docker sandboxing."""
        
        # Docker execution with limits
        docker_cmd = [
            "docker", "run",
            "--rm",
            "--network", "none",  # No network access
            "--memory", "256m",  # Memory limit
            "--cpus", "0.5",  # CPU limit
            "--read-only",  # Read-only filesystem
            "-v", f"{cwd}:/code:ro",  # Mount code directory as read-only
            "-w", "/code",
            "--timeout", str(timeout),
        ]
        
        # Add the actual command
        docker_cmd.extend(cmd)
        
        try:
            process = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdin=asyncio.subprocess.PIPE if stdin_data else None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(stdin_data.encode() if stdin_data else None),
                timeout=timeout + 2,  # Give Docker a bit more time
            )
            
            return process.returncode, stdout.decode(), stderr.decode()
            
        except asyncio.TimeoutError:
            return -1, "", "Docker execution timed out"
            
        except Exception as e:
            return -1, "", str(e)


class SandboxedCompiler(BaseTool):
    """Sandboxed compiler and execution tool."""
    
    name = "compile"
    description = """Compile and run code in multiple languages with sandboxing.
    
    Actions:
    - compile: Compile source code
    - run: Compile and run code
    - evaluate: Evaluate expression
    - test: Run with test cases
    - benchmark: Run performance benchmark
    
    Supported languages: C, C++, Go, JavaScript, TypeScript, Rust, Zig, Python, Java, Ruby
    
    Safety features:
    - Memory limits (256MB default)
    - CPU time limits (10s default)
    - No network access in sandbox mode
    - Read-only filesystem in Docker mode
    """
    
    def __init__(self, use_docker: bool = False):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.executor = SandboxExecutor(use_docker)
        self.use_docker = use_docker
        
    def _detect_language(self, code: str, language: Optional[str] = None) -> Optional[Language]:
        """Detect language from code or hint."""
        
        if language:
            # Try to match language string
            for lang in Language:
                if language.lower() in [lang.value, lang.name.lower()]:
                    return lang
        
        # Auto-detect from code patterns
        patterns = {
            Language.C: ["#include <stdio.h>", "int main("],
            Language.CPP: ["#include <iostream>", "using namespace std", "std::"],
            Language.GO: ["package main", "func main()", "import ("],
            Language.JAVASCRIPT: ["console.log", "function ", "const ", "let ", "var "],
            Language.TYPESCRIPT: ["interface ", "type ", ": string", ": number"],
            Language.RUST: ["fn main()", "let mut ", "impl ", "trait "],
            Language.ZIG: ["pub fn main()", "const std ="],
            Language.PYTHON: ["def ", "import ", "from ", "print("],
            Language.JAVA: ["public class ", "public static void main"],
            Language.RUBY: ["puts ", "def ", "class ", "require "],
        }
        
        for lang, markers in patterns.items():
            if any(marker in code for marker in markers):
                return lang
        
        return None
    
    async def _compile_code(
        self,
        code: str,
        language: Language,
        output_dir: Path,
    ) -> Tuple[bool, str, str]:
        """Compile source code."""
        
        config = COMPILER_CONFIGS[language]
        
        # Write source file
        source_file = output_dir / f"main{config.file_extension}"
        source_file.write_text(code)
        
        if not config.needs_compilation:
            return True, "", ""
        
        # Prepare compile command
        output_file = output_dir / "program"
        compile_cmd = [
            part.replace("{input}", str(source_file))
                .replace("{output}", str(output_file))
            for part in config.compiler_cmd
        ]
        
        # Compile
        returncode, stdout, stderr = await self.executor.execute(
            compile_cmd,
            str(output_dir),
            timeout=30,  # Longer timeout for compilation
        )
        
        return returncode == 0, stdout, stderr
    
    async def _run_code(
        self,
        language: Language,
        output_dir: Path,
        stdin_data: Optional[str] = None,
        timeout: int = 10,
    ) -> Tuple[int, str, str]:
        """Run compiled code."""
        
        config = COMPILER_CONFIGS[language]
        
        if config.needs_compilation:
            output_file = "program"
        else:
            output_file = f"main{config.file_extension}"
        
        # Prepare run command
        run_cmd = [
            part.replace("{input}", output_file)
                .replace("{output}", output_file)
                .replace("{classname}", "main")  # For Java
            for part in config.run_cmd
        ]
        
        # Run
        return await self.executor.execute(
            run_cmd,
            str(output_dir),
            timeout=timeout,
            stdin_data=stdin_data,
        )
    
    async def _run_test_cases(
        self,
        code: str,
        language: Language,
        test_cases: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Run code with multiple test cases."""
        
        results = []
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            
            # Compile once
            success, compile_out, compile_err = await self._compile_code(
                code, language, output_dir
            )
            
            if not success:
                return [{
                    "error": "Compilation failed",
                    "stdout": compile_out,
                    "stderr": compile_err,
                }]
            
            # Run test cases
            for i, test_case in enumerate(test_cases):
                stdin = test_case.get("input", "")
                expected = test_case.get("expected", "")
                
                returncode, stdout, stderr = await self._run_code(
                    language, output_dir, stdin
                )
                
                # Check result
                passed = (
                    returncode == 0 and
                    (not expected or stdout.strip() == expected.strip())
                )
                
                results.append({
                    "test_case": i + 1,
                    "input": stdin,
                    "expected": expected,
                    "actual": stdout.strip(),
                    "stderr": stderr,
                    "passed": passed,
                    "exit_code": returncode,
                })
        
        return results
    
    async def _benchmark_code(
        self,
        code: str,
        language: Language,
        iterations: int = 10,
    ) -> Dict[str, Any]:
        """Benchmark code performance."""
        
        import time
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            
            # Compile
            success, compile_out, compile_err = await self._compile_code(
                code, language, output_dir
            )
            
            if not success:
                return {
                    "error": "Compilation failed",
                    "stdout": compile_out,
                    "stderr": compile_err,
                }
            
            # Run multiple times
            times = []
            for _ in range(iterations):
                start = time.perf_counter()
                returncode, stdout, stderr = await self._run_code(
                    language, output_dir
                )
                elapsed = time.perf_counter() - start
                
                if returncode != 0:
                    return {
                        "error": "Execution failed",
                        "stdout": stdout,
                        "stderr": stderr,
                    }
                
                times.append(elapsed)
            
            # Calculate statistics
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            return {
                "iterations": iterations,
                "average_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "times": times,
                "unit": "seconds",
            }
    
    async def run(
        self,
        action: str,
        code: str,
        language: Optional[str] = None,
        input: Optional[str] = None,
        test_cases: Optional[List[Dict[str, str]]] = None,
        timeout: int = 10,
        iterations: int = 10,
        **kwargs,
    ) -> MCPResourceDocument:
        """Execute compiler action."""
        
        # Detect language
        lang = self._detect_language(code, language)
        
        if not lang:
            return MCPResourceDocument(
                data={
                    "error": "Could not detect language",
                    "hint": "Specify language or use clearer code patterns",
                    "supported_languages": [l.value for l in Language],
                }
            )
        
        if action == "compile":
            # Compile only
            with tempfile.TemporaryDirectory() as tmpdir:
                output_dir = Path(tmpdir)
                success, stdout, stderr = await self._compile_code(
                    code, lang, output_dir
                )
                
                return MCPResourceDocument(
                    data={
                        "success": success,
                        "language": lang.value,
                        "stdout": stdout,
                        "stderr": stderr,
                    }
                )
        
        elif action == "run":
            # Compile and run
            with tempfile.TemporaryDirectory() as tmpdir:
                output_dir = Path(tmpdir)
                
                # Compile
                success, compile_out, compile_err = await self._compile_code(
                    code, lang, output_dir
                )
                
                if not success:
                    return MCPResourceDocument(
                        data={
                            "success": False,
                            "language": lang.value,
                            "phase": "compilation",
                            "stdout": compile_out,
                            "stderr": compile_err,
                        }
                    )
                
                # Run
                returncode, stdout, stderr = await self._run_code(
                    lang, output_dir, input, timeout
                )
                
                return MCPResourceDocument(
                    data={
                        "success": returncode == 0,
                        "language": lang.value,
                        "exit_code": returncode,
                        "stdout": stdout,
                        "stderr": stderr,
                        "compile_output": compile_out,
                    }
                )
        
        elif action == "evaluate":
            # Quick evaluation (for expressions)
            # Wrap code in minimal boilerplate
            if lang == Language.PYTHON:
                wrapped = f"print({code})"
            elif lang == Language.JAVASCRIPT:
                wrapped = f"console.log({code})"
            elif lang == Language.GO:
                wrapped = f"package main\nimport \"fmt\"\nfunc main() {{ fmt.Println({code}) }}"
            else:
                wrapped = code
            
            with tempfile.TemporaryDirectory() as tmpdir:
                output_dir = Path(tmpdir)
                
                success, compile_out, compile_err = await self._compile_code(
                    wrapped, lang, output_dir
                )
                
                if not success:
                    return MCPResourceDocument(
                        data={
                            "success": False,
                            "language": lang.value,
                            "error": compile_err,
                        }
                    )
                
                returncode, stdout, stderr = await self._run_code(
                    lang, output_dir, timeout=5
                )
                
                return MCPResourceDocument(
                    data={
                        "success": returncode == 0,
                        "language": lang.value,
                        "result": stdout.strip(),
                        "stderr": stderr,
                    }
                )
        
        elif action == "test":
            # Run with test cases
            if not test_cases:
                return MCPResourceDocument(
                    data={"error": "Test cases required for test action"}
                )
            
            results = await self._run_test_cases(code, lang, test_cases)
            
            passed = sum(1 for r in results if r.get("passed", False))
            total = len(results)
            
            return MCPResourceDocument(
                data={
                    "language": lang.value,
                    "passed": passed,
                    "total": total,
                    "success": passed == total,
                    "results": results,
                }
            )
        
        elif action == "benchmark":
            # Benchmark performance
            result = await self._benchmark_code(code, lang, iterations)
            
            return MCPResourceDocument(
                data={
                    "language": lang.value,
                    **result,
                }
            )
        
        else:
            return MCPResourceDocument(
                data={
                    "error": f"Unknown action: {action}",
                    "valid_actions": ["compile", "run", "evaluate", "test", "benchmark"],
                }
            )
    
    async def call(self, **kwargs) -> str:
        """Tool interface for MCP."""
        result = await self.run(**kwargs)
        return result.to_json_string()


# Factory function
def create_sandboxed_compiler(use_docker: bool = False):
    """Create sandboxed compiler tool."""
    return SandboxedCompiler(use_docker)