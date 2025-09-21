from .surface import surface
from . import pygame


class font:
    def __init__(self, path):
        self._path = path

    def _font(self, size):
        return pygame.font.Font(self._path, size)

    def render(
        self,
        text,
        size,
        color,
        newLineSpace=5,
        italic=False,
        bold=False,
        underline=False,
    ):
        text = str(text)
        font = self._font(size)
        font.set_italic(italic)
        font.set_bold(bold)
        font.set_underline(underline)
        if text.replace("\n", "") != text:
            text = text.split("\n")
            surf = pygame.Surface(
                [
                    font.size(max(text, key=lambda x: font.size(x)[0]))[0],
                    (font.size("123")[1] + newLineSpace) * len(text),
                ],
                pygame.SRCALPHA,
            )
            y = 0
            for i in text:
                r = font.render(i, True, color)
                surf.blit(r, (0, y))
                y += font.size(i)[1]
                if i != text[-1]:
                    y += newLineSpace
        else:
            surf = font.render(text, True, color)
        surface2 = surface(surf.get_size())
        surface2._surface_orig = surf
        return surface2

    def size(
        self, text, size, newLineSpace=5, italic=False, bold=False, underline=False
    ):
        return self.render(
            text,
            size,
            (255, 255, 255),
            newLineSpace=newLineSpace,
            italic=italic,
            bold=bold,
            underline=underline,
        ).size


class sysFont(font):
    def __init__(self, name):
        self._path = pygame.font.match_font(name)


defaultFont = font(pygame.font.get_default_font())
