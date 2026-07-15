"""Compatibility shim for the package-style layout."""

from src.IServAPI import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("_")]
