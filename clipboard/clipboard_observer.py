from abc import ABC, abstractmethod


class ClipboardObserver(ABC):
    @abstractmethod
    def updateClipboard(self, isEmpty: bool) -> None:
        pass
