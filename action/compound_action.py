from action.edit_action import EditAction


class CompoundAction(EditAction):
    def __init__(self, actions: list[EditAction]) -> None:
        self.actions: list[EditAction] = actions

    def executeDo(self) -> None:
        for action in self.actions:
            action.executeDo()

    def executeUndo(self) -> None:
        for action in reversed(self.actions):
            action.executeUndo()
