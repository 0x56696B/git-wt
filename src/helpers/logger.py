import os
from logging import basicConfig

import click
from rich.console import Console
from rich.logging import RichHandler

console = Console(stderr=True)  # Shared


def setup_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()

    basicConfig(
        level=level,
        format="[%(funcName)s] %(message)s" if level == "DEBUG" else "%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                show_path=True,
                level=level,
                show_time=True,
                show_level=True,
                omit_repeated_times=False,
                tracebacks_show_locals=True,
                tracebacks_suppress=[click],
            )
        ],
    )
