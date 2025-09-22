"""Legacy Web MCP package."""

from __future__ import annotations

from importlib import metadata

__all__ = ["__version__"]

try:
    __version__ = metadata.version("legacy-web-mcp")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
