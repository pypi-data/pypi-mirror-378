from ...image import load as _l
from .base import widget


class image(widget):
    def __init__(self, path):
        self.surface = _l(path)
