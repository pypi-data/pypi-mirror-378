from . import pygame
from .surface import surface
from PIL import Image
import tempfile
import pickle
import bz2
import os


def load(path):
    if path.endswith(".gif"):
        im = Image.open(path)
        with tempfile.TemporaryDirectory() as td:
            surfs = []
            for i in range(im.n_frames):
                im.seek(i)
                p = os.path.join(td, f"{i}.png")
                im.save(p)
                s = pygame.image.load(p)
                os.remove(p)
                sg = surface(s.get_size())
                sg.blit(s, (0, 0))
                surfs.append(sg)
        return surfs
    else:
        im = Image.open(path.encode("utf8").decode("utf8"))
        image = pygame.image.fromstring(im.tobytes(), im.size, im.mode)
        surf = surface(im.size)
        surf.blit(image, (0, 0))
        return surf


def save(surf, dest):
    pygame.image.save_extended(surf._grp(), dest)


def toBytes(surf):
    return bz2.compress(
        pickle.dumps([pygame.image.tostring(surf._grp(), "RGBA"), list(surf.size)])
    )


def fromBytes(bytes):
    string = pickle.loads(bz2.decompress(bytes))
    surf = pygame.image.fromstring(string[0], tuple(string[1]), "RGBA")
    surface2 = surface(tuple(string[1]))
    surface2.blit(surf, (0, 0))
    return surface2
