from ... import pygame
from ...surface import surface as _s
from ...font import deaultFont as _df
from ...rect import rect as _r
from ... import mouse as _m
from ... import keyboard as _k
from ... import pes as _ct
from .base import widget


class entry(widget):
    def __init__(
        self,
        hint="",
        fontSize=30,
        font=_df,
        width=None,
        height=None,
        hide=False,
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
        self.text = ""
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
                if not self.hide:
                    text = self.font.render(self.hint, self.fontSize, self.hintColor)
                else:
                    text = self.font.render(
                        "*" * len(self.hint), self.fontSize, self.hintColor
                    )
            else:
                if not self.hide:
                    text = self.font.render(self.text, self.fontSize, self.afg)
                else:
                    text = self.font.render(
                        "*" * len(self.text), self.fontSize, self.afg
                    )
            x = 10
            if text.size[0] >= self.surface.size[0] - 20:
                x = self.surface.size[0] - text.size[0] - 10
            self.surface.blit(text, (x, self.surface.size[1] / 2 - text.size[1] / 2))
            for i in _k.getPressed().items():
                if i[1]:
                    if i[0] not in self.wclk:
                        if len(i[0]) == 1:
                            self.insert(i[0])
                        elif i[0] == "backspace":
                            self.delete()
                        elif i[0] == "return":
                            self.focus = False
                        elif i[0] == "space":
                            self.insert(" ")
                        self.wclk.append(i[0])
                else:
                    if i[0] in self.wclk:
                        self.wclk.remove(i[0])
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
                if not self.hide:
                    text = self.font.render(self.hint, self.fontSize, self.hintColor)
                else:
                    text = self.font.render(
                        "*" * len(self.hint), self.fontSize, self.hintColor
                    )
            else:
                if self.hide:
                    text = self.font.render(self.text, self.fontSize, self.fg)
                else:
                    text = self.font.render(
                        "*" * len(self.text), self.fontSize, self.fg
                    )
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

    def insert(self, text):
        if _ct.WinDLL("User32.dll").GetKeyState(0x14):
            text = text.upper()
        if (
            hex(getattr(_ct.windll.LoadLibrary("user32.dll"), "GetKeyboardLayout")(0))
            == "0x4190419"
        ):
            text = text.translate(
                dict(
                    zip(
                        map(
                            ord,
                            """qwertyuiop[]asdfghjkl;'zxcvbnm,./`QWERTYUIOPASDFGHJKLZXCVBNM""",
                        ),
                        """йцукенгшщзхъфывапролджэячсмитьбю.ёЙЦУКЕНГШЩЗФЫВАПРОЛДЯЧСМИТЬ""",
                    )
                )
            )
        if (
            pygame.key.get_pressed()[pygame.K_LSHIFT]
            or pygame.key.get_pressed()[pygame.K_RSHIFT]
        ):
            text = text.translate(
                dict(
                    zip(
                        map(ord, """1234567890-=[]\;',./`"""),
                        """!@#$%^&*()_+{}|:"<>?~""",
                    )
                )
            )
        if text in self.blacklist:
            return
        if self.whitelist is not None:
            if text not in self.whitelist:
                return
        if self.maxSymbols is not None:
            if len(self.text) > self.maxSymbols:
                return
        self.text += text

    def delete(self, symbols=1):
        self.text = self.text[: 0 - symbols]

    def draw(self, win, pos):
        self._generate(pos)
        win.blit(self.surface, pos)

    def get(self):
        return self.text
