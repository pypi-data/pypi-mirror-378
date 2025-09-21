"""
Utility functions for PDF reader MCP server.
"""

import os
import sys
from pathlib import Path
from typing import Union


class SecurityError(Exception):
    """Raised when a security violation is detected."""
    pass


class PathUtils:
    """Path utilities with security checks."""

    def __init__(self):
        """Initialize with project root from current working directory."""
        self.project_root = Path.cwd().resolve()
        print(f"[PDF Reader MCP] Project root: {self.project_root}", file=sys.stderr)

    def resolve_path(self, user_path: str) -> Path:
        """
        Resolve a user-provided relative path against the project root.

        Args:
            user_path: The relative path provided by the user

        Returns:
            Resolved absolute path

        Raises:
            SecurityError: If path is absolute or attempts path traversal
            ValueError: If path is invalid
        """
        if not isinstance(user_path, str):
            raise ValueError("Path must be a string")

        if not user_path.strip():
            raise ValueError("Path cannot be empty")

        # Normalize the path
        normalized_path = os.path.normpath(user_path)

        # Check for absolute paths
        if os.path.isabs(normalized_path):
            raise SecurityError("Absolute paths are not allowed")

        # Resolve against project root
        resolved_path = (self.project_root / normalized_path).resolve()

        # Security check: ensure resolved path is within project root
        try:
            resolved_path.relative_to(self.project_root)
        except ValueError:
            raise SecurityError("Path traversal detected. Access denied")

        return resolved_path

    def is_safe_path(self, path: Union[str, Path]) -> bool:
        """
        Check if a path is safe (within project boundaries).

        Args:
            path: Path to check

        Returns:
            True if path is safe, False otherwise
        """
        try:
            if isinstance(path, str):
                self.resolve_path(path)
            else:
                path.resolve().relative_to(self.project_root)
            return True
        except (SecurityError, ValueError):
            return False


def format_error_for_amazon_q(error: Exception, context: str = "") -> str:
    """
    Format error messages in a way that's clear for Amazon Q CLI users.

    Args:
        error: The exception that occurred
        context: Additional context about when the error occurred

    Returns:
        Formatted error message
    """
    error_type = type(error).__name__

    if isinstance(error, SecurityError):
        return f"🔒 Security Error: {str(error)}"
    elif isinstance(error, FileNotFoundError):
        return f"📁 File Not Found: {str(error)}"
    elif isinstance(error, PermissionError):
        return f"🚫 Permission Error: {str(error)}"
    elif "PDF" in str(error).upper():
        return f"📄 PDF Processing Error: {str(error)}"
    else:
        prefix = f"{context}: " if context else ""
        return f"❌ {error_type}: {prefix}{str(error)}"


def truncate_text(text: str, max_length: int = 10000) -> str:
    """
    Truncate text to a maximum length, adding ellipsis if needed.
    Optimized for Amazon Q CLI display.

    Args:
        text: Text to truncate
        max_length: Maximum length (default: 10000 for Q CLI)

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length-3] + "..."


def clean_pdf_text(text: str) -> str:
    """
    Clean extracted PDF text by removing excessive whitespace
    and normalizing line breaks for better Amazon Q CLI display.

    Args:
        text: Raw text from PDF

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Replace multiple whitespace characters with single space
    import re
    cleaned = re.sub(r'\s+', ' ', text)

    # Remove excessive line breaks but preserve paragraph structure
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)

    return cleaned.strip()