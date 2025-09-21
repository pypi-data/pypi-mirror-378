from .rect import rect
from .color import color
from . import pygame


class surface:
    def __init__(self, size):
        self._size = size
        self._orig = pygame.Surface(size, pygame.SRCALPHA)

    @property
    def pixels(self):
        pixels = []
        for x in range(self.size[0]):
            pixels.append([])
            for y in range(self.size[1]):
                pixels[x].append(self.getPixel(x, y))
        return pixels

    @property
    def size(self):
        return self._size

    def _grp(self):
        return self._orig

    def rect(self, x=0, y=0, center=[]):
        if center == []:
            return rect(x, y, self.size[0], self.size[1])
        else:
            return rect(
                center[0] - (self.size[0] / 2),
                center[1] - (self.size[1] / 2),
                self.size[0],
                self.size[1],
            )

    def copy(self):
        surf = surface(self._size)
        surf._surface_orig = self._orig
        surf._surface_size = self._size
        return surf

    def getPixel(self, x, y):
        return color(*self._orig.get_at((x, y)))

    def setPixel(self, x, y, color):
        self._orig.set_at((x, y), color)
        return self.copy()

    def blit(self, surf, xy):
        if type(surf) is not surface and type(surf) is pygame.Surface:
            from pygwin.font import defaultFont as _df

            surf = _df.render(surf, 25, (0, 0, 0))
        try:
            self._orig.blit(surf._surface_orig, xy)
        except Exception as _:
            try:
                self._orig.blit(surf._orig, xy)
            except Exception as _:
                self._orig.blit(surf, xy)
        return self.copy()

    def fill(self, color):
        self._orig.fill(list(color))
        return self.copy()

    def crop(self, rect):
        self._orig = self._orig.subsurface(rect)
        self._size = self._orig.get_size()
        return self.copy()

    def scale(self, size, smooth=False):
        if not smooth:
            self._orig = pygame.transform.scale(self._orig, size)
        else:
            self._orig = pygame.transform.smoothscale(self._orig, size)
        self._size = self._orig.get_size()
        return self.copy()

    def rotate(self, angle):
        self._orig = pygame.transform.rotate(self._orig, angle)
        self._size = self._orig.get_size()
        return self.copy()

    def flip(self, x, y):
        self._orig = pygame.transform.flip(self._orig, x, y)
        return self.copy()

    def blur(self, amt):
        if amt < 0:
            return self.copy()
        scale = (
            int(self._orig.get_width() * (amt + 1)),
            int(self._orig.get_height() * (amt + 1)),
        )
        size = self._orig.get_size()
        self._orig = pygame.transform.smoothscale(self._orig, scale)
        self._orig = pygame.transform.smoothscale(self._orig, size)
        return self.copy()

    class _draw:
        def __init__(self, surface):
            self._surf = surface

        def rect(
            self,
            color,
            rect,
            width=0,
            borderRadius=0,
            borderTopLeftRadius=-1,
            borderTopRightRadius=-1,
            borderBottomLeftRadius=-1,
            borderBottomRightRadius=-1,
        ):
            try:
                orig = self._surf._surface_orig
            except Exception as _:
                orig = self._surf._orig
            pygame.draw.rect(
                orig,
                color,
                pygame.Rect(rect[0], rect[1], rect[2], rect[3]),
                width,
                borderRadius,
                borderTopLeftRadius,
                borderTopRightRadius,
                borderBottomLeftRadius,
                borderBottomRightRadius,
            )
            return self._surf.copy()

        def polygon(self, color, points, width=0):
            try:
                orig = self._surf._surface_orig
            except Exception as _:
                orig = self._surf._orig
            pygame.draw.polygon(orig, color, points, width)
            return self._surf.copy()

        def circle(
            self,
            color,
            center,
            radius,
            width=0,
            drawTopLeft=1,
            drawTopRight=1,
            drawBottomLeft=1,
            drawBottomRight=1,
        ):
            try:
                orig = self._surf._surface_orig
            except Exception as _:
                orig = self._surf._orig
            pygame.draw.circle(
                orig,
                color,
                center,
                radius,
                width,
                drawTopRight,
                drawTopLeft,
                drawBottomLeft,
                drawBottomRight,
            )
            return self._surf.copy()

        def ellipse(self, color, rect, width=0):
            try:
                orig = self._surf._surface_orig
            except Exception as _:
                orig = self._surf._orig
            pygame.draw.ellipse(
                orig, color, pygame.Rect(rect[0], rect[1], rect[2], rect[3]), width
            )
            return self._surf.copy()

        def line(self, color, start, end, width=1):
            try:
                orig = self._surf._surface_orig
            except Exception as _:
                orig = self._surf._orig
            pygame.draw.line(orig, color, start, end, width)
            return self._surf.copy()

        def arc(self, color, rect, startAngle, stopAngle, width=1):
            try:
                orig = self._surf._surface_orig
            except Exception as _:
                orig = self._surf._orig
            pygame.draw.arc(
                orig,
                color,
                pygame.Rect(rect[0], rect[1], rect[2], rect[3]),
                startAngle,
                stopAngle,
                width,
            )
            return self._surf.copy()

    @property
    def draw(self):
        return self._draw(self)
