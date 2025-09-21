"""
Public API for koegelbrunf.

Attempts to import the Cython backend; if unavailable, falls back to the
pure-Python implementation with identical behavior.
"""

import warnings

try:  # Prefer compiled extension if present
    from ._square import square  # type: ignore[attr-defined]
    USING_CYTHON = True
except Exception:  # ImportError or runtime loader issues
    from ._square_py import square  # pure-Python fallback
    USING_CYTHON = False
    warnings.warn(
        "koegelbrunf: using pure-Python fallback; install a compiler for Cython speed.",
        RuntimeWarning,
        stacklevel=2,
    )

__all__ = ["square", "USING_CYTHON"]
