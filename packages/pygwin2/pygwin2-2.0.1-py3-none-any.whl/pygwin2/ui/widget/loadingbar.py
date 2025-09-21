from ...surface import surface as _s
from ...rect import rect as _r
from .base import widget


class loadingBar(widget):
    def __init__(
        self,
        width,
        height=50,
        length=100,
        bg=(70, 70, 70),
        loadedColor=(50, 200, 50),
        borderColor=(50, 50, 50),
        borderWidth=5,
    ):
        super()._args(locals())
        self.loaded = 0

    def step(self, count=1):
        self.loaded += 1
        if self.loaded > self.length:
            self.loaded = self.length

    def set(self, x):
        self.loaded = x
        if self.loaded > self.length:
            self.loaded = self.length

    def reset(self):
        self.loaded = 0

    def get(self):
        return self.loaded

    def draw(self, win, pos):
        self.surface = _s((self.width, self.height))
        self.surface.fill(self.borderColor)
        self.surface.draw.rect(
            self.bg, _r(5, 5, self.surface.size[0] - 10, self.surface.size[1] - 10)
        )
        self.surface.draw.rect(
            self.loadedColor,
            _r(
                self.borderWidth,
                self.borderWidth,
                (self.surface.size[0] / self.length * self.loaded)
                - self.borderWidth * 2,
                self.surface.size[1] - self.borderWidth * 2,
            ),
        )
        win.blit(self.surface, pos)
