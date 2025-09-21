from . import pygame


def getPressed():
    orig = pygame.mouse.get_pressed(3)
    return {"left": orig[0], "middle": orig[1], "right": orig[2]}


def isPressed(x):
    return getPressed()[x.lower()]


def setPosition(x):
    pygame.mouse.set_pos(x)


def getPosition():
    return pygame.mouse.get_pos()


def setVisible(x):
    pygame.mouse.set_visible(x)


def getVisible():
    return pygame.mouse.get_visible()


def getCursor():
    return pygame.mouse.get_cursor()


def setCursor(size, hotspot=None, xormasks=None, andmasks=None):
    if hotspot is None and xormasks is None and andmasks is None:
        pygame.mouse.set_system_cursor(size)
    else:
        pygame.mouse.set_cursor(size, hotspot, xormasks, andmasks)
