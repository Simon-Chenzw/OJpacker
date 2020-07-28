from __future__ import absolute_import

import sys
import time
from functools import partial
from typing import Union

from rich.console import Console
from rich.progress import BarColumn, Progress, TimeRemainingColumn

#console
console = Console(
    file=sys.stderr,
    log_path=False,
)

# rich print
rprint = console.log

# log
error = partial(console.log, "[red]ERROR[/red]  ")
warning = partial(console.log, "[yellow]WARNING[/yellow]")
info = partial(console.log, "[blue]INFO[/blue]   ")
debug = partial(console.log, "[green]DEBUG[/green]  ")

log_level = 10
level_table = {
    "error": 40,
    "warning": 30,
    "info": 20,
    "debug": 10,
}

# progress
progress = partial(
    Progress,
    " " * 15,
    "[progress.description]{task.description:10}",
    BarColumn(),
    "{task.completed} of {task.total}",
    console=console,
)
unknown_progress = partial(
    Progress,
    " " * 15,
    "[progress.description]{task.description:10}",
    BarColumn(),
    console=console,
)


def countdown(second: int) -> None:
    with Progress(
            " " * 15,
            "[progress.description]{task.description:10}",
            TimeRemainingColumn(),
            console=console,
            transient=True,
    ) as progress:
        mask = progress.add_task(
            "     [cyan]Countdown[/cyan]",
            total=second * 20 - 10,
            start=False,
        )
        progress.start_task(mask)
        for _ in range(second * 20):
            progress.advance(mask)
            time.sleep(0.05)


def set_log_level(level: Union[int, str] = 20, ) -> None:
    global error, warning, info, debug

    if isinstance(level, str):
        level = level.lower()
        if level.lower() in level_table:
            level = level.lower()
        else:
            warning("unknown log level, use info")
            level = "info"
        level = level_table[level]

    NONE = partial(lambda *args, **kwargs: None)

    error = partial(console.log, "[red]ERROR[/red]  ") if level <= 40 else NONE
    warning = partial(console.log,
                      "[yellow]WARNING[/yellow]") if level <= 30 else NONE
    info = partial(console.log,
                   "[blue]INFO[/blue]   ") if level <= 20 else NONE
    debug = partial(console.log,
                    "[green]DEBUG[/green]  ") if level <= 10 else NONE
