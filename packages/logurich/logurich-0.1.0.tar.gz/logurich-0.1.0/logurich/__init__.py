__version__ = "0.1.0"

from .console import console, configure_console, get_console, rich_to_str, set_console
from .core import (
    ContextValue,
    ctx,
    global_configure,
    global_set_context,
    init_logger,
    logger,
    mp_configure,
)

init_logger("INFO")

__all__ = [
    "logger",
    "init_logger",
    "mp_configure",
    "global_configure",
    "global_set_context",
    "ContextValue",
    "ctx",
    "console",
    "configure_console",
    "get_console",
    "set_console",
    "rich_to_str",
]
