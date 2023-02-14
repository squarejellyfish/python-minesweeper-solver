class Tile:
    def __init__(self, state, position, flaged=False) -> None:
        self.state = state
        self.position = position
        self.marked = False
        self.flaged = True if flaged else False
        self.cleaned = False

    def __eq__(self, other):
        if not isinstance(other, Tile):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.position == other.position

    def __hash__(self) -> int:
        return hash((self.state, self.position))

    def isMarked(self):
        return self.marked

    def mark(self):
        self.marked = True

    def isFlaged(self):
        return self.flaged

    def flag(self):
        self.flaged = True

    def isCleaned(self):
        return self.cleaned

    def isCovered(self):
        return self.state == None

    def clean(self):
        self.cleaned = True

    def isNumber(self):
        return self.state > 0 and self.state < 10
