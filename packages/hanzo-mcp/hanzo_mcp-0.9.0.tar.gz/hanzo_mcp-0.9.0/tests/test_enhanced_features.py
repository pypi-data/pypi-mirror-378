"""Tests for enhanced features including LSP, environment detection, compiler, and memory."""

import json
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock

from hanzo_mcp.tools.lsp.enhanced_lsp import EnhancedLSPTool, Language
from hanzo_mcp.tools.environment.environment_detector import EnvironmentDetector
from hanzo_mcp.tools.framework.framework_modes import FrameworkModeManager
from hanzo_mcp.tools.compiler.sandboxed_compiler import SandboxedCompiler
from hanzo_mcp.tools.memory.conversation_memory import ConversationMemory, MessageRole


class TestEnhancedLSP:
    """Test enhanced LSP implementation."""
    
    def test_language_detection(self):
        """Test language detection from file extensions."""
        tool = EnhancedLSPTool()
        
        assert tool._detect_language("test.c") == "c"
        assert tool._detect_language("test.cpp") == "cpp"
        assert tool._detect_language("test.go") == "go"
        assert tool._detect_language("test.js") == "javascript"
        assert tool._detect_language("test.ts") == "typescript"
        assert tool._detect_language("test.rs") == "rust"
        assert tool._detect_language("test.zig") == "zig"
        assert tool._detect_language("test.py") == "python"
        assert tool._detect_language("unknown.xyz") is None
    
    def test_project_root_detection(self):
        """Test project root finding."""
        tool = EnhancedLSPTool()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create markers
            (tmpdir_path / "go.mod").touch()
            src_dir = tmpdir_path / "src"
            src_dir.mkdir()
            test_file = src_dir / "test.go"
            test_file.touch()
            
            # Should find go.mod
            root = tool._find_project_root(str(test_file), "go")
            assert root == str(tmpdir_path)
    
    @pytest.mark.asyncio
    async def test_compile_action(self):
        """Test compilation action."""
        tool = EnhancedLSPTool()
        
        # Test simple C code
        code = '#include <stdio.h>\nint main() { printf("Hello\\n"); return 0; }'
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.c"
            test_file.write_text(code)
            
            with patch("asyncio.create_subprocess_exec") as mock_exec:
                mock_process = AsyncMock()
                mock_process.communicate = AsyncMock(return_value=(b"", b""))
                mock_process.returncode = 0
                mock_exec.return_value = mock_process
                
                result = await tool.run(
                    action="compile",
                    file=str(test_file)
                )
                
                assert "success" in result.data
    
    @pytest.mark.asyncio
    async def test_run_action(self):
        """Test run action."""
        tool = EnhancedLSPTool()
        
        # Test Python code (no compilation needed)
        code = 'print("Hello from Python")'
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(code)
            
            with patch("asyncio.create_subprocess_exec") as mock_exec:
                mock_process = AsyncMock()
                mock_process.communicate = AsyncMock(
                    return_value=(b"Hello from Python\n", b"")
                )
                mock_process.returncode = 0
                mock_exec.return_value = mock_process
                
                result = await tool.run(
                    action="run",
                    file=str(test_file)
                )
                
                assert result.data["success"] is True
                assert "Hello from Python" in result.data["stdout"]


class TestEnvironmentDetector:
    """Test environment detection tool."""
    
    def test_tool_detection(self):
        """Test detecting installed tools."""
        detector = EnvironmentDetector()
        
        with patch.object(detector, "_run_command") as mock_run:
            # Mock Python detection
            mock_run.return_value = "Python 3.9.0"
            
            detection = detector._detect_tool("python", {
                "check_cmd": ["python", "--version"],
                "category": "language",
                "mcp_tools": ["run_command"],
                "parse_version": lambda out: out.split()[1] if out else None,
            })
            
            assert detection is not None
            assert detection.name == "python"
            assert detection.version == "3.9.0"
            assert detection.category == "language"
    
    def test_framework_detection(self):
        """Test framework detection."""
        detector = EnvironmentDetector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            detector.project_root = Path(tmpdir)
            
            # Create package.json with Next.js
            package_json = {
                "dependencies": {
                    "next": "^13.0.0"
                }
            }
            (detector.project_root / "package.json").write_text(
                json.dumps(package_json)
            )
            
            # Check framework detection
            assert detector._check_file_content("package.json", "next") is True
    
    def test_suggest_tools(self):
        """Test tool suggestions based on project."""
        detector = EnvironmentDetector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            detector.project_root = Path(tmpdir)
            
            # Create project files
            (detector.project_root / "package.json").touch()
            (detector.project_root / "requirements.txt").touch()
            
            suggestions = detector.suggest_tools()
            
            # Should suggest node and python if not detected
            detector.detected_tools = []  # No tools detected
            suggestions = detector.suggest_tools()
            assert "node" in suggestions["languages"] or "python" in suggestions["languages"]
    
    def test_configuration_generation(self):
        """Test MCP configuration generation."""
        detector = EnvironmentDetector()
        
        # Add mock detections
        from hanzo_mcp.tools.environment.environment_detector import ToolDetection
        
        detector.detected_tools = [
            ToolDetection(
                name="python",
                version="3.9.0",
                path="/usr/bin/python",
                category="language",
                mcp_tools=["run_command", "uvx"]
            ),
            ToolDetection(
                name="node",
                version="16.0.0",
                path="/usr/bin/node",
                category="language",
                mcp_tools=["npx"]
            )
        ]
        
        config = detector.generate_configuration()
        
        assert "python" in config["modes"]
        assert "javascript" in config["modes"]
        assert "run_command" in config["enabled_mcp_tools"]
        assert "uvx" in config["enabled_mcp_tools"]
        assert "npx" in config["enabled_mcp_tools"]


class TestFrameworkModes:
    """Test framework-specific mode management."""
    
    def test_mode_enabling(self):
        """Test enabling framework modes."""
        manager = FrameworkModeManager()
        
        result = manager.enable_mode("django")
        
        assert result["success"] is True
        assert "django" in manager.active_modes
        assert "python" in manager.active_modes  # Dependency
        assert "django_manage" in result["enabled_tools"]
    
    def test_mode_dependencies(self):
        """Test mode dependency resolution."""
        manager = FrameworkModeManager()
        
        # Django depends on Python
        result = manager.enable_mode("django")
        
        assert "python" in result["dependencies_enabled"]
        assert "python" in manager.active_modes
    
    def test_mode_disabling(self):
        """Test disabling modes."""
        manager = FrameworkModeManager()
        
        # Enable modes
        manager.enable_mode("fastapi")
        manager.enable_mode("python")
        
        # Disable Python (fastapi depends on it)
        result = manager.disable_mode("python")
        
        assert result["success"] is True
        assert "fastapi" in result["dependent_modes_disabled"]
        assert "python" not in manager.active_modes
        assert "fastapi" not in manager.active_modes
    
    def test_snippet_retrieval(self):
        """Test getting code snippets."""
        manager = FrameworkModeManager()
        
        snippet = manager.get_snippet("django", "model")
        assert "class" in snippet
        assert "models.Model" in snippet
        
        snippet = manager.get_snippet("nextjs", "page")
        assert "export default function" in snippet
    
    def test_command_retrieval(self):
        """Test getting framework commands."""
        manager = FrameworkModeManager()
        
        cmd = manager.get_command("django", "serve")
        assert cmd == ["python", "manage.py", "runserver"]
        
        cmd = manager.get_command("rust", "build")
        assert cmd == ["cargo", "build"]
    
    def test_mode_listing(self):
        """Test listing available modes."""
        manager = FrameworkModeManager()
        
        # List all modes
        modes = manager.list_modes()
        assert len(modes) > 0
        
        # List by category
        web_modes = manager.list_modes(category="web")
        assert all(m["category"] == "web" for m in web_modes)
        
        language_modes = manager.list_modes(category="language")
        assert all(m["category"] == "language" for m in language_modes)


class TestSandboxedCompiler:
    """Test sandboxed compilation and execution."""
    
    def test_language_detection_from_code(self):
        """Test detecting language from code patterns."""
        compiler = SandboxedCompiler()
        
        # C code
        c_code = '#include <stdio.h>\nint main() {}'
        assert compiler._detect_language(c_code) == Language.C
        
        # Python code
        py_code = 'def main():\n    print("Hello")'
        assert compiler._detect_language(py_code) == Language.PYTHON
        
        # Go code
        go_code = 'package main\nfunc main() {}'
        assert compiler._detect_language(go_code) == Language.GO
        
        # Rust code
        rust_code = 'fn main() {\n    println!("Hello");\n}'
        assert compiler._detect_language(rust_code) == Language.RUST
    
    @pytest.mark.asyncio
    async def test_compile_c_code(self):
        """Test compiling C code."""
        compiler = SandboxedCompiler()
        
        code = '''
#include <stdio.h>
int main() {
    printf("Hello, World!\\n");
    return 0;
}
'''
        
        with patch.object(compiler.executor, "execute") as mock_exec:
            mock_exec.return_value = (0, "", "")
            
            result = await compiler.run(
                action="compile",
                code=code,
                language="c"
            )
            
            assert result.data["success"] is True
            assert result.data["language"] == "c"
    
    @pytest.mark.asyncio
    async def test_run_python_code(self):
        """Test running Python code."""
        compiler = SandboxedCompiler()
        
        code = 'print("Hello from Python")'
        
        with patch.object(compiler.executor, "execute") as mock_exec:
            mock_exec.return_value = (0, "Hello from Python\n", "")
            
            result = await compiler.run(
                action="run",
                code=code,
                language="python"
            )
            
            assert result.data["success"] is True
            assert "Hello from Python" in result.data["stdout"]
    
    @pytest.mark.asyncio
    async def test_evaluate_expression(self):
        """Test evaluating expressions."""
        compiler = SandboxedCompiler()
        
        with patch.object(compiler.executor, "execute") as mock_exec:
            mock_exec.return_value = (0, "42\n", "")
            
            result = await compiler.run(
                action="evaluate",
                code="6 * 7",
                language="python"
            )
            
            assert result.data["success"] is True
            assert "42" in result.data["result"]
    
    @pytest.mark.asyncio
    async def test_run_with_test_cases(self):
        """Test running code with test cases."""
        compiler = SandboxedCompiler()
        
        code = '''
n = int(input())
print(n * 2)
'''
        
        test_cases = [
            {"input": "5", "expected": "10"},
            {"input": "7", "expected": "14"},
            {"input": "0", "expected": "0"},
        ]
        
        with patch.object(compiler, "_compile_code") as mock_compile:
            mock_compile.return_value = (True, "", "")
            
            with patch.object(compiler, "_run_code") as mock_run:
                mock_run.side_effect = [
                    (0, "10\n", ""),
                    (0, "14\n", ""),
                    (0, "0\n", ""),
                ]
                
                result = await compiler.run(
                    action="test",
                    code=code,
                    language="python",
                    test_cases=test_cases
                )
                
                assert result.data["passed"] == 3
                assert result.data["total"] == 3
                assert result.data["success"] is True


class TestConversationMemory:
    """Test conversation memory with vector search."""
    
    @pytest.mark.asyncio
    async def test_add_message(self):
        """Test adding messages to conversation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = ConversationMemory(storage_path=tmpdir)
            
            message = await memory.add_message(
                role="user",
                content="Hello, how are you?",
                metadata={"timestamp": "2024-01-01"}
            )
            
            assert message.role == MessageRole.USER
            assert message.content == "Hello, how are you?"
            assert message.embedding is not None
            assert len(memory.current_conversation.messages) == 1
    
    @pytest.mark.asyncio
    async def test_search_messages(self):
        """Test searching messages with vector similarity."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = ConversationMemory(storage_path=tmpdir)
            
            # Add messages
            await memory.add_message("user", "How do I use Python?")
            await memory.add_message("assistant", "Python is a programming language.")
            await memory.add_message("user", "Can you help with JavaScript?")
            await memory.add_message("assistant", "JavaScript is used for web development.")
            
            # Search for Python-related messages
            results = await memory.search_messages("Python programming", limit=2)
            
            assert len(results) > 0
            # First result should be Python-related
            assert "Python" in results[0][0].content
    
    @pytest.mark.asyncio
    async def test_conversation_summary(self):
        """Test generating conversation summaries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = ConversationMemory(storage_path=tmpdir)
            
            # Add conversation
            await memory.add_message("user", "What is machine learning?")
            await memory.add_message("assistant", "Machine learning is important for AI.")
            await memory.add_message("user", "How does it work?")
            await memory.add_message("assistant", "It works through training on data.")
            
            summary = await memory.summarize_conversation()
            
            assert summary is not None
            assert len(summary) > 0
    
    @pytest.mark.asyncio
    async def test_topic_extraction(self):
        """Test extracting topics from conversation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = ConversationMemory(storage_path=tmpdir)
            
            # Add messages about programming
            await memory.add_message("user", "Python programming tutorial")
            await memory.add_message("assistant", "Python is great for beginners")
            await memory.add_message("user", "JavaScript frameworks")
            await memory.add_message("assistant", "React and Vue are popular")
            
            topics = await memory.extract_topics()
            
            assert len(topics) > 0
            # Should include programming-related topics
    
    def test_export_conversations(self):
        """Test exporting conversations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = ConversationMemory(storage_path=tmpdir)
            
            # Add a message
            asyncio.run(memory.add_message("user", "Test message"))
            
            # Export as JSON
            export = memory.export_conversations(format="json")
            
            assert "conversations" in export
            assert len(export["conversations"]) == 1
            
            # Export as Markdown
            export = memory.export_conversations(format="markdown")
            
            assert "content" in export
            assert "Conversation" in export["content"]
    
    def test_statistics(self):
        """Test getting memory statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = ConversationMemory(storage_path=tmpdir)
            
            # Add messages
            asyncio.run(memory.add_message("user", "Question 1"))
            asyncio.run(memory.add_message("assistant", "Answer 1"))
            
            stats = memory.get_statistics()
            
            assert stats["total_conversations"] == 1
            assert stats["total_messages"] == 2
            assert stats["role_distribution"]["user"] == 1
            assert stats["role_distribution"]["assistant"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])