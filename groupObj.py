class Group:

    def __init__(self, cells=list, mines=int, type="exactly") -> None:
        self.cells = set(cells)
        self.mines = mines
        self.type = type

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Group):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.cells == other.cells

    def __hash__(self) -> int:

        return hash((self.cells, self.mines))

    def add(self, cells=list, active_mines=int):
        self.cells.append(cells)
        self.mines = active_mines

    def diff(self, cell):
        cells = self.cells.copy()
        cells.remove(cell)
        return cells
