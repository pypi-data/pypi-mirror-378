"""Compatibility shim.

The implementation previously lived here; it has been merged into
`modern_server.py` for easier single-file debugging. Importing run_test from
this module still works.
"""
from .modern_server import run_test  # re-export

__all__ = ["run_test"]
