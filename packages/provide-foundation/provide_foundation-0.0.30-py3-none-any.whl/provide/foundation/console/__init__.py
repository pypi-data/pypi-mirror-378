from __future__ import annotations

from provide.foundation.console.input import (
    apin,
    apin_lines,
    apin_stream,
    pin,
    pin_lines,
    pin_stream,
)
from provide.foundation.console.output import perr, pout

"""Console I/O utilities for standardized CLI input/output.

Provides pout(), perr(), and pin() functions for consistent I/O handling.
"""

__all__ = [
    # Async input functions
    "apin",
    "apin_lines",
    "apin_stream",
    # Output functions
    "perr",
    # Input functions
    "pin",
    "pin_lines",
    "pin_stream",
    "pout",
]
