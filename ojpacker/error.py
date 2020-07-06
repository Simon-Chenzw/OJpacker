from __future__ import absolute_import

from typing import Optional


class OjpackerError(Exception):
    def __init__(self, message: Optional[str] = None):
        self.message = message or "An error has occurred"

    def __str__(self) -> str:
        return self.message
