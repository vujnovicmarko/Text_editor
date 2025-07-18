from location.location import Location


class LocationRange:
    def __init__(
        self, start: Location = Location(), end: Location = Location()
    ) -> None:
        self.start: Location = start
        self.end: Location = end

    def getCoords(self) -> tuple[int, int, int, int]:
        start_coords = self.start.getCoords()
        end_coords = self.end.getCoords()

        if start_coords > end_coords:
            start_coords, end_coords = end_coords, start_coords

        return start_coords + end_coords
