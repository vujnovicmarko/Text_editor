from clipboard.clipboard_observer import ClipboardObserver


class ClipboardStack:
    def __init__(self) -> None:
        self.texts: list[str] = []
        self.clipboardObservers: list[ClipboardObserver] = []

    def push(self, text: str) -> None:
        self.texts.append(text)
        self.notifyClipboardObservers()

    def pop(self) -> str:
        if not self.isEmpty():
            text = self.texts.pop()
            self.notifyClipboardObservers()
            return text
        else:
            raise IndexError("Clipboard empty")

    def peek(self) -> str:
        if not self.isEmpty():
            return self.texts[-1]
        else:
            raise IndexError("Clipboard empty")

    def isEmpty(self) -> bool:
        return len(self.texts) == 0

    def clear(self) -> None:
        self.texts = []
        self.notifyClipboardObservers()

    def addClipboardObserver(self, clipboardObserver: ClipboardObserver) -> None:
        self.clipboardObservers.append(clipboardObserver)

    def removeClipboardObserver(self, clipboardObserver: ClipboardObserver) -> None:
        self.clipboardObservers.remove(clipboardObserver)

    def notifyClipboardObservers(self) -> None:
        for clipboardObserver in self.clipboardObservers:
            clipboardObserver.updateClipboard(len(self.texts) == 0)
