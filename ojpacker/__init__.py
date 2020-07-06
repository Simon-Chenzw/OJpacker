from __future__ import absolute_import

from typing import Optional, Sequence, Text

from ojpacker.error import OjpackerError

from . import arg, ui


def main(argv: Optional[Sequence[Text]] = None) -> None:
    """
    main function, try to catch expected error
    """
    try:
        arg.analyze(argv)
    except OjpackerError as err:
        ui.error(str(err))
    except SystemExit:
        # ui.debug("catch SystemExit")
        pass
    except KeyboardInterrupt:
        ui.debug("catch KeyboardInterrupt")
    except:
        ui.console.print_exception()
