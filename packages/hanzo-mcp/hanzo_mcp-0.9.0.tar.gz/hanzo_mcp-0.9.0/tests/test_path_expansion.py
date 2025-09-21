"""Test path expansion functionality for filesystem tools."""

import os
import tempfile
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch
from hanzo_mcp.tools.filesystem.read import ReadTool
from hanzo_mcp.tools.filesystem.write import Write
from hanzo_mcp.tools.filesystem.edit import EditTool
from hanzo_mcp.tools.filesystem.multi_edit import MultiEditTool
from hanzo_mcp.tools.common.permissions import PermissionManager


@pytest.fixture
def permission_manager():
    """Create a permission manager with test paths allowed."""
    pm = PermissionManager()
    # Add home directory and test paths
    pm.add_allowed_path(str(Path.home()))
    pm.add_allowed_path("/tmp")
    pm.add_allowed_path(tempfile.gettempdir())
    return pm


@pytest.fixture
def mock_ctx():
    """Create a mock MCP context."""
    return MagicMock()


@pytest.mark.asyncio
async def test_read_tool_tilde_expansion(permission_manager, mock_ctx):
    """Test that ReadTool correctly expands tilde (~) in paths."""
    read_tool = ReadTool(permission_manager)
    
    # Create a test file in home directory
    test_file = Path.home() / "test_read_expansion.txt"
    test_content = "Test content for tilde expansion"
    
    try:
        # Write test file
        test_file.write_text(test_content)
        
        # Test reading with tilde path
        result = await read_tool.call(
            mock_ctx,
            file_path="~/test_read_expansion.txt"
        )
        
        # Verify content was read (will have line numbers)
        assert "Test content for tilde expansion" in result
        assert "1" in result  # Line number should be present
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


@pytest.mark.asyncio
async def test_write_tool_tilde_expansion(permission_manager, mock_ctx):
    """Test that Write tool correctly expands tilde (~) in paths."""
    write_tool = Write(permission_manager)
    
    # Test file path with tilde
    test_file = Path.home() / "test_write_expansion.txt"
    test_content = "Written with tilde expansion"
    
    try:
        # Write using tilde path
        result = await write_tool.call(
            mock_ctx,
            file_path="~/test_write_expansion.txt",
            content=test_content
        )
        
        # Verify success
        assert "Successfully wrote file" in result
        
        # Verify file exists and has correct content
        assert test_file.exists()
        assert test_file.read_text() == test_content
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


@pytest.mark.asyncio
async def test_environment_variable_expansion(permission_manager, mock_ctx):
    """Test that paths with environment variables are expanded correctly."""
    read_tool = ReadTool(permission_manager)
    
    # Set a test environment variable
    test_dir = str(Path.home())
    os.environ["TEST_HOME_DIR"] = test_dir
    
    # Create a test file
    test_file = Path(test_dir) / "test_env_expansion.txt"
    test_content = "Environment variable expansion test"
    
    try:
        # Write test file
        test_file.write_text(test_content)
        
        # Test reading with environment variable
        result = await read_tool.call(
            mock_ctx,
            file_path="$TEST_HOME_DIR/test_env_expansion.txt"
        )
        
        # Verify content was read
        assert "Environment variable expansion test" in result
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if "TEST_HOME_DIR" in os.environ:
            del os.environ["TEST_HOME_DIR"]


@pytest.mark.asyncio
async def test_edit_tool_tilde_expansion(permission_manager, mock_ctx):
    """Test that EditTool correctly expands tilde (~) in paths."""
    edit_tool = EditTool(permission_manager)
    
    # Create a test file in home directory
    test_file = Path.home() / "test_edit_expansion.txt"
    original_content = "Original content to be edited"
    
    try:
        # Write test file
        test_file.write_text(original_content)
        
        # Edit using tilde path
        result = await edit_tool.call(
            mock_ctx,
            file_path="~/test_edit_expansion.txt",
            old_string="Original content",
            new_string="Modified content"
        )
        
        # Verify success
        assert "Successfully replaced" in result or "applied" in result.lower()
        
        # Verify file was edited
        new_content = test_file.read_text()
        assert "Modified content" in new_content
        assert "Original content" not in new_content
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


@pytest.mark.asyncio
async def test_multi_edit_tool_tilde_expansion(permission_manager, mock_ctx):
    """Test that MultiEditTool correctly expands tilde (~) in paths."""
    multi_edit_tool = MultiEditTool(permission_manager)
    
    # Create a test file in home directory
    test_file = Path.home() / "test_multi_edit_expansion.txt"
    original_content = "Line 1: First\nLine 2: Second\nLine 3: Third"
    
    try:
        # Write test file
        test_file.write_text(original_content)
        
        # Multi-edit using tilde path
        result = await multi_edit_tool.call(
            mock_ctx,
            file_path="~/test_multi_edit_expansion.txt",
            edits=[
                {"old_string": "First", "new_string": "Modified First"},
                {"old_string": "Second", "new_string": "Modified Second"}
            ]
        )
        
        # Verify success
        assert "Successfully applied" in result
        
        # Verify file was edited
        new_content = test_file.read_text()
        assert "Modified First" in new_content
        assert "Modified Second" in new_content
        assert "First" not in new_content
        assert "Second" not in new_content
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


@pytest.mark.asyncio
async def test_permission_manager_tilde_expansion():
    """Test that PermissionManager correctly expands tilde in allowed paths."""
    pm = PermissionManager()
    
    # Add home directory using tilde
    pm.add_allowed_path("~/test_directory")
    
    # Test that expanded path is allowed
    test_path = str(Path.home() / "test_directory" / "file.txt")
    assert pm.is_path_allowed(test_path)
    
    # Test that tilde path is also allowed (should be expanded)
    assert pm.is_path_allowed("~/test_directory/file.txt")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])