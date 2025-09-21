__all__ = [
    "pygame",
    "tray",
    "rect",
    "surface",
    "console",
    "color",
    "keyboard",
    "mouse",
    "mixer",
    "image",
    "font",
    "ui",
]

from . import pygame
from .pygame.locals import *
from .tray import tray
from .rect import rect
from .surface import surface
from .console import console
from .color import color
from .window import *
from . import keyboard
from . import mouse
from . import image
from . import mixer
from . import font
from . import ui
from . import gamepad as _gp

gamepad = _gp.gamepad(pygame)
