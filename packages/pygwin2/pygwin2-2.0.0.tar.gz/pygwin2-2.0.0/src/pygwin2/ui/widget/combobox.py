from ...surface import surface as _s
from ...font import deaultFont as _df
from .base import widget


class comboBox(widget):
    def __init__(
        self,
        text,
        values=[],
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
        self._generate()

    def _generate(self, position=None):
        self.surface = _s((255, self.width))

    def draw(self, win, pos):
        self._generate(pos)
        win.blit(self.surface, pos)
