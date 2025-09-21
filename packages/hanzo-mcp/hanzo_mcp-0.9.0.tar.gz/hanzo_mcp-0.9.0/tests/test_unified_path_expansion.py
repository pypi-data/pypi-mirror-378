#!/usr/bin/env python3
"""Comprehensive test for unified path expansion across all filesystem tools."""

import os
import tempfile
from pathlib import Path
import pytest
from unittest.mock import MagicMock
from hanzo_mcp.tools.common.permissions import PermissionManager
from hanzo_mcp.tools.common.path_utils import resolve_path

# Import all filesystem tools
from hanzo_mcp.tools.filesystem.read import ReadTool
from hanzo_mcp.tools.filesystem.write import Write
from hanzo_mcp.tools.filesystem.edit import EditTool
from hanzo_mcp.tools.filesystem.multi_edit import MultiEditTool
from hanzo_mcp.tools.filesystem.directory_tree import DirectoryTreeTool
from hanzo_mcp.tools.filesystem.find import FindTool
from hanzo_mcp.tools.filesystem.search import SearchTool  # Renamed from grep
from hanzo_mcp.tools.filesystem.ast_tool import ASTTool
from hanzo_mcp.tools.filesystem.git_search import GitSearchTool


@pytest.fixture
def permission_manager():
    """Create a permission manager with test paths allowed."""
    pm = PermissionManager()
    # Add home directory and all common test paths
    pm.add_allowed_path(str(Path.home()))
    pm.add_allowed_path("/tmp")
    pm.add_allowed_path(tempfile.gettempdir())
    return pm


@pytest.fixture
def mock_ctx():
    """Create a mock MCP context."""
    return MagicMock()


@pytest.fixture
def test_directory():
    """Create a test directory structure in home directory."""
    test_dir = Path.home() / "test_path_expansion"
    test_dir.mkdir(exist_ok=True)
    
    # Create test files
    (test_dir / "test_file.txt").write_text("Test content")
    (test_dir / "test_code.py").write_text("def test():\n    pass")
    
    yield test_dir
    
    # Cleanup
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)


class TestCentralizedPathResolution:
    """Test the centralized resolve_path function."""
    
    def test_tilde_expansion(self):
        """Test that tilde (~) is expanded to home directory."""
        result = resolve_path("~/test/file.txt")
        expected = str(Path.home() / "test" / "file.txt")
        assert result == expected
    
    def test_environment_variable_expansion(self):
        """Test that environment variables are expanded."""
        os.environ["TEST_DIR"] = "/tmp/test"
        result = resolve_path("$TEST_DIR/file.txt")
        assert result == str(Path("/tmp/test/file.txt").resolve())
        del os.environ["TEST_DIR"]
    
    def test_combined_expansion(self):
        """Test combined tilde and environment variable expansion."""
        os.environ["HOME_ALIAS"] = "~"
        result = resolve_path("$HOME_ALIAS/test.txt")
        expected = str(Path.home() / "test.txt")
        assert result == expected
        del os.environ["HOME_ALIAS"]
    
    def test_absolute_path_unchanged(self):
        """Test that absolute paths are resolved but structure preserved."""
        result = resolve_path("/tmp/test/file.txt")
        expected = str(Path("/tmp/test/file.txt").resolve())
        assert result == expected
    
    def test_relative_path_resolution(self):
        """Test that relative paths are resolved to absolute."""
        original_dir = os.getcwd()
        os.chdir("/tmp")
        result = resolve_path("./test.txt")
        expected = str(Path("/tmp/test.txt").resolve())
        assert result == expected
        os.chdir(original_dir)


@pytest.mark.asyncio
class TestFileSystemToolsPathExpansion:
    """Test path expansion in all filesystem tools."""
    
    async def test_read_tool(self, permission_manager, mock_ctx, test_directory):
        """Test ReadTool with tilde path."""
        read_tool = ReadTool(permission_manager)
        
        # Test with tilde path
        result = await read_tool.call(
            mock_ctx,
            file_path="~/test_path_expansion/test_file.txt"
        )
        
        assert "Test content" in result
        assert "Error" not in result
    
    async def test_write_tool(self, permission_manager, mock_ctx, test_directory):
        """Test Write tool with tilde path."""
        write_tool = Write(permission_manager)
        
        # Test with tilde path
        result = await write_tool.call(
            mock_ctx,
            file_path="~/test_path_expansion/written.txt",
            content="Written via tilde path"
        )
        
        assert "Successfully wrote" in result
        
        # Verify file exists
        written_file = test_directory / "written.txt"
        assert written_file.exists()
        assert written_file.read_text() == "Written via tilde path"
    
    async def test_edit_tool(self, permission_manager, mock_ctx, test_directory):
        """Test EditTool with tilde path."""
        edit_tool = EditTool(permission_manager)
        
        # Create a file to edit
        test_file = test_directory / "edit_test.txt"
        test_file.write_text("Original text")
        
        # Edit with tilde path
        result = await edit_tool.call(
            mock_ctx,
            file_path="~/test_path_expansion/edit_test.txt",
            old_string="Original",
            new_string="Modified"
        )
        
        assert "Successfully" in result or "replaced" in result.lower()
        assert test_file.read_text() == "Modified text"
    
    async def test_directory_tree_tool(self, permission_manager, mock_ctx, test_directory):
        """Test DirectoryTreeTool with tilde path."""
        tree_tool = DirectoryTreeTool(permission_manager)
        
        # Test with tilde path
        result = await tree_tool.call(
            mock_ctx,
            path="~/test_path_expansion"
        )
        
        assert "test_file.txt" in result
        assert "test_code.py" in result
        assert "Error" not in result
    
    async def test_search_tool(self, permission_manager, mock_ctx, test_directory):
        """Test SearchTool with tilde path."""
        search_tool = SearchTool(permission_manager)
        
        # Test with tilde path
        result = await search_tool.call(
            mock_ctx,
            query="Test",
            path="~/test_path_expansion"
        )
        
        # Should find matches
        assert "test_file.txt" in result or "matches" in result.lower()
        assert "Error" not in result
    
    async def test_find_tool(self, permission_manager, mock_ctx, test_directory):
        """Test FindTool with tilde path."""
        find_tool = FindTool(permission_manager)
        
        # Test with tilde path
        result = await find_tool.call(
            mock_ctx,
            pattern="*.txt",
            path="~/test_path_expansion"
        )
        
        assert "test_file.txt" in result
        assert "Error" not in result
    
    async def test_environment_variable_paths(self, permission_manager, mock_ctx, test_directory):
        """Test tools with environment variable paths."""
        # Set environment variable pointing to test directory
        os.environ["TEST_EXPANSION_DIR"] = str(test_directory)
        
        read_tool = ReadTool(permission_manager)
        result = await read_tool.call(
            mock_ctx,
            file_path="$TEST_EXPANSION_DIR/test_file.txt"
        )
        
        assert "Test content" in result
        assert "Error" not in result
        
        del os.environ["TEST_EXPANSION_DIR"]


class TestPermissionManagerPathExpansion:
    """Test PermissionManager handles expanded paths correctly."""
    
    def test_allowed_path_with_tilde(self):
        """Test adding allowed path with tilde."""
        pm = PermissionManager()
        pm.add_allowed_path("~/test_dir")
        
        # Check that expanded path is allowed
        test_file = str(Path.home() / "test_dir" / "file.txt")
        assert pm.is_path_allowed(test_file)
        
        # Check that tilde path also works
        assert pm.is_path_allowed("~/test_dir/file.txt")
    
    def test_excluded_path_with_tilde(self):
        """Test excluding path with tilde."""
        pm = PermissionManager()
        pm.add_allowed_path("~")  # Allow home directory
        pm.exclude_path("~/excluded_dir")
        
        # Check that excluded path is not allowed
        assert not pm.is_path_allowed("~/excluded_dir/file.txt")
        
        # Check that other paths in home are allowed
        assert pm.is_path_allowed("~/other_dir/file.txt")
    
    def test_environment_variable_in_allowed_path(self):
        """Test environment variables in allowed paths."""
        os.environ["TEST_ALLOWED"] = str(Path.home() / "allowed")
        
        pm = PermissionManager()
        pm.add_allowed_path("$TEST_ALLOWED")
        
        # Check that path under env var directory is allowed
        test_path = str(Path.home() / "allowed" / "test.txt")
        assert pm.is_path_allowed(test_path)
        
        del os.environ["TEST_ALLOWED"]


@pytest.mark.asyncio
class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    async def test_double_tilde(self, permission_manager, mock_ctx):
        """Test handling of paths with multiple tildes."""
        read_tool = ReadTool(permission_manager)
        
        # This should fail appropriately
        result = await read_tool.call(
            mock_ctx,
            file_path="~~/invalid/path.txt"
        )
        
        assert "Error" in result or "not exist" in result.lower()
    
    async def test_undefined_environment_variable(self, permission_manager, mock_ctx):
        """Test handling of undefined environment variables."""
        read_tool = ReadTool(permission_manager)
        
        # Undefined env var should remain as-is
        result = await read_tool.call(
            mock_ctx,
            file_path="$UNDEFINED_VAR_XYZ/file.txt"
        )
        
        assert "Error" in result or "not exist" in result.lower()
    
    async def test_mixed_separators(self, permission_manager, mock_ctx, test_directory):
        """Test handling of mixed path separators."""
        write_tool = Write(permission_manager)
        
        # Mix forward and backslashes (will be normalized)
        result = await write_tool.call(
            mock_ctx,
            file_path="~/test_path_expansion/subdir/../mixed.txt",
            content="Mixed separators test"
        )
        
        assert "Successfully wrote" in result
        
        # File should be in test_directory root (.. goes up from subdir)
        mixed_file = test_directory / "mixed.txt"
        assert mixed_file.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])