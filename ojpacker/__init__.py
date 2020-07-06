from __future__ import absolute_import

from . import ui, arg


def main(debug: bool = False) -> None:
    ui.set_log_level("debug" if debug else "info")
    try:
        arg.analyze()
    except SystemExit:
        ui.debug("catch SystemExit")
    except KeyboardInterrupt:
        ui.debug("catch KeyboardInterrupt")
    except:
        ui.console.print_exception()