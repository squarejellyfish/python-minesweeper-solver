class Group:

    def __init__(self, cells: list, mines: int, type="exactly") -> None:
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


class Cluster(Group):

    def __init__(self, cells: list, constraint: int) -> None:
        self.cells = set(cells)
        self.constraint = constraint
        self.groups = []
        self.length = len(cells)
        self.weight = self.length / self.constraint

    def __hash__(self) -> int:

        return hash((self.cells, self.constraint))

    def contains(self, cell: object) -> bool:
        return (cell in self.cells)

    def contains_all(self, cells) -> bool:
        for cell in cells:
            if not self.contains(cell):
                return False

        return True

    def add(self, cells=list):
        for cell in cells:
            self.cells.add(cell)

    def add_constraint(self, constraint):
        self.constraint += constraint

    def add_group(self, group: Group):
        self.groups.append(group)

    def add_groups(self, groups):
        for group in groups:
            self.groups.append(group)

    def get_cells(self):
        return self.cells
