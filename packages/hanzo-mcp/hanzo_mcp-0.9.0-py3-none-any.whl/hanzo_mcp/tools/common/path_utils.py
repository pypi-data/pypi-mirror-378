"""Path utility functions for consistent path handling across MCP tools."""

import os
from pathlib import Path


def resolve_path(path: str) -> str:
    """Resolve a path by expanding user home directory (~) and environment variables.
    
    This is the centralized path resolution function used by all filesystem tools
    to ensure consistent path handling across the MCP system.
    
    Args:
        path: The path to resolve, may contain ~ or environment variables
        
    Returns:
        The fully resolved absolute path
        
    Examples:
        >>> resolve_path('~/Documents/file.txt')
        '/Users/username/Documents/file.txt'
        
        >>> os.environ['MYDIR'] = '/tmp/test'
        >>> resolve_path('$MYDIR/file.txt')
        '/tmp/test/file.txt'
    """
    # First expand environment variables, then user home directory
    # This order is important for cases like $HOME_ALIAS where the env var contains ~
    expanded = os.path.expandvars(path)
    expanded = os.path.expanduser(expanded)
    
    # Convert to Path object and resolve to get absolute path
    # This handles relative paths and resolves symlinks
    return str(Path(expanded).resolve())