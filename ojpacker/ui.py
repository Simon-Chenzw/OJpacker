from __future__ import absolute_import

import sys
import time
from functools import partial, wraps
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
log_level = 10
level_table = {
    "error": 40,
    "warning": 30,
    "info": 20,
    "detail": 10,
    "debug": 0,
}
log_head = {
    "error": "[red]ERROR[/red]  ",
    "warning": "[yellow]WARNING[/yellow]",
    "info": "[blue]INFO[/blue]   ",
    "detail": "[cyan]DETAIl[/cyan] ",
    "debug": "[green]DEBUG[/green]  ",
}

error = partial(console.log, log_head["error"])
warning = partial(console.log, log_head["warning"])
info = partial(console.log, log_head["info"])
detail = partial(console.log, log_head["detail"])
debug = partial(console.log, log_head["debug"])

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


# @log
def log(func):
    @wraps(func)
    def logger(*args, **kwargs):
        debug(
            f"[magenta]{func.__module__[9:]}.{func.__name__}[/magenta]",
            *map(lambda str: f"[cyan]{str}[/cyan]", args),
            *sum(
                map(
                    lambda key: (f"[blue]{key}[/blue]:", kwargs[key]),
                    kwargs,
                ),
                (),
            ),
        )
        ret = func(*args, **kwargs)
        return ret

    return logger


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
    global log_level

    if isinstance(level, str):
        if level.lower() in level_table:
            level = level.lower()
        else:
            # warning("unknown log level, use info")
            level = "info"
        log_level = level_table[level]
    else:
        log_level = level

    for level in level_table:
        if log_level <= level_table[level]:
            globals()[level] = partial(console.log, log_head[level])
        else:
            globals()[level] = partial(lambda *args, **kwargs: None)
