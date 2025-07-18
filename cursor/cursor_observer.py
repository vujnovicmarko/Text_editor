from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from location.location import Location


class CursorObserver(ABC):
    @abstractmethod
    def updateCursorLocation(self, loc: Location) -> None:
        pass
