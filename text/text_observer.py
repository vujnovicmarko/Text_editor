from abc import ABC, abstractmethod


class TextObserver(ABC):
    @abstractmethod
    def updateText(self) -> None:
        pass
