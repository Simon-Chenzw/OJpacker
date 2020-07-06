from __future__ import absolute_import

from . import ui, arg


def main() -> None:
    try:
        arg.analyze()
    except KeyboardInterrupt:
        ui.debug("catch KeyboardInterrupt")
    except:
        ui.console.print_exception()