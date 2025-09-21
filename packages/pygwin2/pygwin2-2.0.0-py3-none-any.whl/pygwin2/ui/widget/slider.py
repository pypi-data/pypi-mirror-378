from ...surface import surface as _s
from ...rect import rect as _r
from ... import mouse as _m
from .base import widget


class slider(widget):
    def __init__(self, width, bg=(70, 70, 70), fg=(200, 200, 200), horizontal=True):
        super()._args(locals())
        self.s = False
        self.x = 12.5
        self._generate(None)

    def _generate(self, pos):
        if self.horizontal:
            self.surface = _s((self.width, 50))
            self.surface.draw.line(self.bg, [12.5, 25], [self.width - 12.5, 25], 10)
            self.surface.draw.circle(self.bg, [12.5, 26], 5)
            self.surface.draw.circle(self.bg, [self.width - 12.5, 26], 5)
            self.surface.draw.circle(self.fg, [self.x, 25], 12.5)
        else:
            self.surface = _s((50, self.width))
            self.surface.draw.line(self.bg, [25, 12.5], [25, self.width - 12.5], 10)
            self.surface.draw.circle(self.bg, [26, 12.5], 5)
            self.surface.draw.circle(self.bg, [26, self.width - 12.5], 5)
            self.surface.draw.circle(self.fg, [25, self.x], 12.5)
        if pos is not None:
            if _m.isPressed("left"):
                if self.horizontal:
                    rect = _r(
                        pos[0] + 5,
                        pos[1],
                        self.surface.size[0] - 10,
                        self.surface.size[1],
                    )
                    if (
                        rect.contains(_m.getPosition()[0], _m.getPosition()[1])
                        or self.s
                    ):
                        self.x = _m.getPosition()[0] - pos[0]
                        if self.x < 12.5:
                            self.x = 12.5
                        if self.x > self.width - 12.5:
                            self.x = self.width - 12.5
                        self.s = True
                else:
                    rect = _r(
                        pos[0],
                        pos[1] + 5,
                        self.surface.size[0],
                        self.surface.size[1] - 10,
                    )
                    if (
                        rect.contains(_m.getPosition()[0], _m.getPosition()[1])
                        or self.s
                    ):
                        self.x = _m.getPosition()[1] - pos[1]
                        if self.x < 12.5:
                            self.x = 12.5
                        if self.x > self.width - 12.5:
                            self.x = self.width - 12.5
                        self.s = True
            else:
                self.s = False

    def get(self):
        return int(self.x / (self.width - 10) * 101)

    def set(self, x):
        self.x = x / 101 * (self.width - 10)

    def draw(self, win, pos):
        self._generate(pos)
        win.blit(self.surface, pos)
