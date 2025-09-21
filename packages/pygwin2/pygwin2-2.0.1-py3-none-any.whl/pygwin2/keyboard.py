from . import pygame


def getPressed():
    fkeys = {}
    keys = pygame.key.get_pressed()
    for i in range(len(keys)):
        fkeys.update({pygame.key.name(i): keys[i]})
    return fkeys


def isPressed(key):
    return getPressed()[key]
