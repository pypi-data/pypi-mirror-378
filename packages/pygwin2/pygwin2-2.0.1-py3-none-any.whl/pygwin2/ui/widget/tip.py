from ...surface import surface as _s
from ...font import deaultFont as _df
from ...rect import rect as _r
from ... import mouse as _m
from .base import widget


class tip(widget):
    def __init__(
        self,
        text,
        responceWidth,
        responceHeight,
        fontSize=15,
        font=_df,
        borderColor=(180, 180, 50),
        borderWidth=2,
        bg=(255, 255, 128),
        fg=(35, 35, 5),
        waitBeforeShowing=0,
        tipPosRelativeCursor=(10, 10),
    ):
        super()._args(locals())
        self.tick = -1
        self.lcp = (0, 0)
        self.tprc = self.tipPosRelativeCursor
        self._generate()

    def _generate(self, position=None):
        self.surface = _s((self.responceWidth, self.responceHeight))
        if position is not None:
            self.tick += 1
            if self.lcp != _m.getPosition():
                self.tick = 0
                self.lcp = _m.getPosition()
            if self.tick >= self.waitBeforeShowing:
                mp = _m.getPosition()
                mp = [
                    mp[0] + self.tprc[0] - position[0],
                    mp[1] + self.tprc[1] - position[1],
                ]
                rect = _r(
                    mp[0],
                    mp[1],
                    self.font.size(self.text, self.fontSize)[0] + 4,
                    self.font.size(self.text, self.fontSize)[1] + 6,
                )
                if mp[0] < 0 or mp[1] < 0:
                    return
                if mp[0] > self.responceWidth:
                    return
                if mp[1] > self.responceHeight:
                    return
                if mp[0] > self.responceWidth - rect.w:
                    mp[0] = self.responceWidth - rect.w
                if mp[1] > self.responceHeight - rect.h:
                    mp[1] = self.responceHeight - rect.h
                rect = _r(
                    mp[0],
                    mp[1],
                    self.font.size(self.text, self.fontSize)[0] + 4,
                    self.font.size(self.text, self.fontSize)[1] + 6,
                )
                self.surface.draw.rect(self.bg, rect)
                self.surface.draw.rect(self.borderColor, rect, self.borderWidth)
                ts = self.font.render(self.text, self.fontSize, self.fg)
                self.surface.blit(ts, (mp[0] + 2, mp[1] + 3))

    def draw(self, win, pos):
        self._generate(pos)
        win.blit(self.surface, pos)
