from ... import pygame
from ...surface import surface as _s
from ...rect import rect as _r
from ... import mouse as _m
from .base import widget


class checkBox(widget):
    def __init__(
        self,
        width=50,
        bg=(180, 180, 180),
        fg=(50, 180, 50),
        afg=(70, 200, 70),
        abg=(120, 120, 120),
        borderColor=(220, 220, 220),
        borderWidth=5,
    ):
        super()._args(locals())
        self.cl0 = False
        self.cl1 = False
        self.nc0 = True
        self.x = False
        self._generate()

    def set(self, x):
        self.x = x

    def get(self):
        return self.x

    def _generate(self, position=None):
        self.surface = _s((self.width, self.width))
        if position is not None:
            contains = self.surface.rect(position[0], position[1]).contains(
                _m.getPosition()[0], _m.getPosition()[1]
            )
            cacm = contains and _m.isPressed("left")
        else:
            contains = False
            cacm = False
        if contains and not self.cl0:
            _m.setCursor(pygame.SYSTEM_CURSOR_HAND)
            self.cl0 = True
            self.nc0 = True
        elif not contains:
            if self.nc0:
                _m.setCursor(pygame.SYSTEM_CURSOR_ARROW)
                self.nc0 = False
            self.cl0 = False
        if cacm and not self.cl1:
            self.x = self.x == 0
            self.cl1 = True
        elif not cacm:
            self.cl1 = False
        self.surface.fill(self.borderColor)
        if cacm:
            self.surface.draw.rect(
                self.abg,
                _r(
                    self.borderWidth,
                    self.borderWidth,
                    self.surface.size[0] - self.borderWidth * 2,
                    self.surface.size[1] - self.borderWidth * 2,
                ),
            )
            if self.x:
                self.surface.draw.line(
                    self.afg,
                    [self.borderWidth, self.width / 2 + self.borderWidth],
                    [self.width / 2, self.width - self.borderWidth],
                    self.borderWidth,
                )
                self.surface.draw.line(
                    self.afg,
                    [self.width / 2, self.width - self.borderWidth],
                    [self.width - self.borderWidth, self.borderWidth],
                    self.borderWidth,
                )
        else:
            self.surface.draw.rect(
                self.bg,
                _r(
                    self.borderWidth,
                    self.borderWidth,
                    self.surface.size[0] - self.borderWidth * 2,
                    self.surface.size[1] - self.borderWidth * 2,
                ),
            )
            if self.x:
                self.surface.draw.line(
                    self.fg,
                    [self.borderWidth, self.width / 2 + self.borderWidth],
                    [self.width / 2, self.width - self.borderWidth],
                    self.borderWidth,
                )
                self.surface.draw.line(
                    self.fg,
                    [self.width / 2, self.width - self.borderWidth],
                    [self.width - self.borderWidth, self.borderWidth],
                    self.borderWidth,
                )

    def draw(self, win, pos):
        self._generate(pos)
        win.blit(self.surface, pos)
