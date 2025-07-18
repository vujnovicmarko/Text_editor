from __future__ import annotations


class Location:
    def __init__(self, row: int = 0, col: int = 0) -> None:
        self.row: int = row
        self.col: int = col

    def getCoords(self) -> tuple[int, int]:
        return (self.row, self.col)

    def __repr__(self) -> str:
        return f"Location: {self.row}, {self.col}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Location):
            return False
        return self.row == other.row and self.col == other.col
