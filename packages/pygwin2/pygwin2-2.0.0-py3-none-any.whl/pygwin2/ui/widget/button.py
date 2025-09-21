from ... import pygame
from ...surface import surface as _s
from ...font import deaultFont as _df
from ...rect import rect as _r
from ... import mouse as _m
from .base import widget


class button(widget):
    def __init__(
        self,
        text,
        func=lambda: None,
        fontSize=30,
        font=_df,
        width=None,
        height=None,
        bg=(70, 70, 70),
        fg=(180, 180, 200),
        afg=(50, 50, 50),
        abg=(200, 200, 200),
        borderColor=(50, 50, 50),
        borderWidth=5,
    ):
        super()._args(locals())
        self.cl0 = False
        self.cl1 = False
        self.nc0 = True
        self._generate()

    def _generate(self, position=None):
        if self.width is None or self.height is None:
            textSize = self.font.size(self.text, self.fontSize)
            if self.width is not None:
                self.surface = _s((self.width, textSize[1] + 10))
            elif self.height is not None:
                self.surface = _s((textSize[0] + 50, self.height))
            else:
                self.surface = _s((textSize[0] + 50, textSize[1] + 10))
        else:
            self.surface = _s((self.width, self.height))
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
            self.func()
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
        if cacm:
            text = self.font.render(self.text, self.fontSize, self.afg)
        else:
            text = self.font.render(self.text, self.fontSize, self.fg)
        pos = text.rect(center=(self.surface.size[0] / 2, self.surface.size[1] / 2))
        pos = [pos.x, pos.y]
        self.surface.blit(text, pos)

    def draw(self, win, pos):
        self._generate(pos)
        win.blit(self.surface, pos)
