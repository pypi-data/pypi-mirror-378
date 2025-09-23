class TapeArray:
    def __init__(self, blank=None):
        self.blank = blank
        self.cells = {}

    def __getitem__(self, index):
        # просто возвращаем blank, но не добавляем ключ
        return self.cells.get(index) if index in self.cells else self.blank

    def __setitem__(self, index, value):
        self.cells[index] = value

    def __contains__(self, index):
        return index in self.cells

    def __repr__(self):
        if not self.cells:
            return "<empty tape>"
        lo, hi = min(self.cells), max(self.cells)
        return " ".join(
            str(self.cells.get(i) if i in self.cells and self.cells[i] is not None else "_")
            for i in range(lo, hi + 1)
        )

    @property
    def end(self):
        return max(self.cells)

    @property
    def start(self):
        return min(self.cells)