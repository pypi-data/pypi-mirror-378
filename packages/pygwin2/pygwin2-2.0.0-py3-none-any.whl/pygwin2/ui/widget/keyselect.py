from ... import pygame
from ...surface import surface as _s
from ...font import deaultFont as _df
from ...rect import rect as _r
from ... import mouse as _m
from ... import keyboard as _k
from .entry import entry


class keySelect(entry):
    def __init__(
        self,
        keyBefore="",
        fontSize=30,
        font=_df,
        width=None,
        height=None,
        bg=(70, 70, 70),
        fg=(180, 180, 200),
        afg=(200, 200, 200),
        abg=(50, 50, 50),
        hintColor=(100, 100, 100),
        lineColor=(200, 200, 200),
        borderColor=(50, 50, 50),
        borderWidth=5,
        maxSymbols=None,
        whitelist=None,
        blacklist=[],
    ):
        super()._args(locals())
        self.hint = ""
        self.text = keyBefore
        self.focus = False
        self.tick = 0
        self.wcl = False
        self.startHint = self.hint
        self.ws = False
        if self.width is None or self.height is None:
            if self.hint != "":
                hintSize = self.font.size(self.hint, self.fontSize)
            else:
                hintSize = (150, self.font.size("X", self.fontSize)[1])
            if self.height is None:
                self.height = hintSize[1] + 10
            if self.width is None:
                self.width = hintSize[0] + 50
        self.surface = _s((self.width, self.height))
        self.wclk = []
        self.wsnr = False

    def _generate(self, position=None):
        self.surface.fill(self.borderColor)
        if self.focus:
            self.surface.draw.rect(
                self.abg,
                _r(
                    self.borderWidth,
                    self.borderWidth,
                    self.surface.size[0] - self.borderWidth * 2,
                    self.surface.size[1] - self.borderWidth * 2,
                ),
            )
            if self.text == "":
                text = self.font.render(self.hint, self.fontSize, self.hintColor)
            else:
                text = self.font.render(self.text, self.fontSize, self.afg)
            x = self.surface.size[0] / 2 - text.size[0] / 2
            if text.size[0] >= self.surface.size[0] - 20:
                x = self.surface.size[0] - text.size[0] - 10
            self.surface.blit(text, (x, self.surface.size[1] / 2 - text.size[1] / 2))
            for i in _k.getPressed().items():
                if i[1] and self.focus:
                    if i[0] in self.blacklist:
                        continue
                    if self.whitelist is not None:
                        if i[0] not in self.whitelist:
                            continue
                    if self.maxSymbols is not None:
                        if len(self.text) > self.maxSymbols:
                            continue
                    self.text = i[0]
                    break
            self.tick += 1
            if self.tick >= 60:
                if self.text != "":
                    points = [
                        [x + text.size[0], self.surface.size[1] / 2 - text.size[1] / 2],
                        [
                            x + text.size[0],
                            self.surface.size[1] / 2
                            - text.size[1] / 2
                            + self.surface.size[1]
                            - 10,
                        ],
                    ]
                    self.surface.draw.line(self.lineColor, points[0], points[1], 3)
            if self.tick == 120:
                self.tick = 0
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
            if self.text == "":
                text = self.font.render(self.hint, self.fontSize, self.hintColor)
            else:
                text = self.font.render(self.text, self.fontSize, self.fg)
            x = self.surface.size[0] / 2 - text.size[0] / 2
            if text.size[0] >= self.surface.size[0] - 20:
                x = self.surface.size[0] - text.size[0] - 10
            self.surface.blit(text, (x, self.surface.size[1] / 2 - text.size[1] / 2))

        if position is not None:
            if self.surface.rect(position[0], position[1]).contains(
                _m.getPosition()[0], _m.getPosition()[1]
            ):
                if not self.wcl:
                    _m.setCursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    if not self.ws:
                        _m.setCursor(pygame.SYSTEM_CURSOR_ARROW)
                        self.ws = True
                if _m.isPressed("left"):
                    if not self.wcl:
                        self.focus = self.focus == 0
                        self.wcl = True
                else:
                    self.wcl = False
                self.wsnr = False
            else:
                if not self.wsnr:
                    _m.setCursor(pygame.SYSTEM_CURSOR_ARROW)
                    self.wsnr = True
                if _m.isPressed("left"):
                    self.focus = False

    def draw(self, win, pos):
        self._generate(pos)
        win.blit(self.surface, pos)

    def get(self):
        return self.text
