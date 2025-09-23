"""
tinyargs - Ultra-light command-line argument grabber for quick scripts.

Public API:
    - get()   -> fetch a single argument by key
    - flag()  -> check if a boolean flag is present
    - args()  -> fetch multiple arguments at once
    - TinyArgsError -> raised on missing/invalid args
"""

from .core import get, flag, args, TinyArgsError

__all__ = ["get", "flag", "args", "TinyArgsError"]

__version__ = "0.1.0"
