from __future__ import absolute_import

import shlex
from typing import Sequence, Text, Union

from . import arg, ui
from .error import OjpackerError


def start(argv: Union[Sequence[Text], Text, None] = None) -> None:
    """
    main function, try to catch expected error
    """
    try:
        if isinstance(argv, Text):
            argv = shlex.split(argv)
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
        exit(1)
