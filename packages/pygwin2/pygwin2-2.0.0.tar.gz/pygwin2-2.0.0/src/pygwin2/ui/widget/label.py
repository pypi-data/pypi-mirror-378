from ...font import deaultFont as _df
from .base import widget


class label(widget):
    def __init__(self, text, size=30, color=(0, 0, 0), font=_df):
        self.surface = font.render(text, size, color)
