class SaturatingNumber:
    def __init__(self, inner, min, max):
        self.inner = inner
        self.min = min
        self.max = max

    def add(self, other):
        self.inner = min(self.inner + other, self.max)

    def sub(self, other):
        self.inner = max(self.inner - other, self.min)

    @property
    def is_max(self):
        return self.inner == self.max

    @property
    def is_min(self):
        return self.inner == self.min
