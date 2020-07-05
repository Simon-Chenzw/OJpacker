from __future__ import absolute_import

import sys
from functools import partial
from typing import Dict, Union

from rich.console import Console
from rich.progress import BarColumn, Progress

#console
console = Console(
    file=sys.stderr,
    log_path=False,
)

# rich print
rprint = console.log

# log
error = partial(console.log, "[red]ERROR[/red]  :")
warning = partial(console.log, "[yellow]WARNING[/yellow]:")
info = partial(console.log, "[blue]INFO[/blue]   :")
debug = partial(console.log, "[green]DEBUG[/green]  :")

# progress
progress = partial(
    Progress,
    " " * 10,
    "[progress.description]{task.description:10}",
    BarColumn(),
    "{task.completed} of {task.total}",
    console=console,
)
unknown_progress = partial(
    Progress,
    " " * 10,
    "[progress.description]{task.description:10}",
    BarColumn(),
    console=console,
)


def set_log_level(level: Union[int, str] = 20, ) -> None:

    if isinstance(level, str):
        level = level.lower()
        level_table: Dict[str, int] = {
            "error": 40,
            "warning": 30,
            "info": 20,
            "debug": 10,
        }
        if level in level_table:
            level = level_table[level]

    NONE = lambda *args, **kwargs: None

    global error, warning, info, debug
    error = partial(console.log,
                    "[red]ERROR[/red]  :") if level <= 40 else NONE
    warning = partial(console.log,
                      "[yellow]WARNING[/yellow]:") if level <= 30 else NONE
    info = partial(console.log,
                   "[blue]INFO[/blue]   :") if level <= 20 else NONE
    debug = partial(console.log,
                    "[green]DEBUG[/green]  :") if level <= 10 else NONE
