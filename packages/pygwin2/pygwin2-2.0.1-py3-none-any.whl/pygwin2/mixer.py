from . import pygame
import os
import tempfile

ffmpeg = None


class sound:
    def __init__(self, path):
        if not (path.endswith(".wav") or path.endswith(".ogg")):
            try:
                from pydub import AudioSegment

                if ffmpeg is not None:
                    AudioSegment.ffmpeg = ffmpeg
                    AudioSegment.converter = ffmpeg
                sound = AudioSegment.from_file(path, os.path.splitext(path)[1])
                path = tempfile.mkstemp(".wav")
                sound.export(path, format="wav")
            except Exception as _:
                print(
                    "Set ffmpeg to path so that you don"
                    + "'t have to convert the file to "
                    + '".wav". If you have installed, but the error still appears, write down the path to ffmpeg.exe in plugin.ffmpeg.'
                )
        self._sound = pygame.mixer.Sound(path)

    def play(self):
        self._sound.play()

    def stop(self):
        self._sound.stop()

    def volume():
        def fget(self):
            return self._sound.get_volume()

        def fset(self, value):
            if type(value) is int:
                self._sound.set_volume(value)

        def fdel(self):
            pass

        return locals()

    volume = property(**volume())

    @property
    def length(self):
        return self._sound.get_length()


class music:
    def __init__(self, path):
        if path.endswith(".wav") or path.endswith(".ogg"):
            self._path = path
        else:
            try:
                from pydub import AudioSegment

                if ffmpeg is not None:
                    AudioSegment.ffmpeg = ffmpeg
                    AudioSegment.converter = ffmpeg
                sound = AudioSegment.from_file(path, os.path.splitext(path)[1])
                path = tempfile.mkstemp(".wav")
                sound.export(path, format="wav")
            except Exception as _:
                print(
                    "Set ffmpeg to path so that you don"
                    + "'t have to convert the file to "
                    + '".wav". If you have installed, but the error still appears, write down the path to ffmpeg.exe in plugin.ffmpeg.'
                )
        pygame.mixer.music.load(path)

    def play(self, loops=0):
        pygame.mixer.music.play(loops)

    def stop(self):
        pygame.mixer.music.stop()

    def restart(self):
        pygame.mixer.music.rewind()

    def pause(self):
        pygame.mixer.music.pause()

    def release(self):
        pygame.mixer.music.unpause()

    def queue(self):
        pygame.mixer.music.queue(self._path)

    def volume():
        def fget(self):
            return pygame.mixer.music.get_volume()

        def fset(self, value):
            if type(value) is int:
                pygame.mixer.music.set_volume(value)

        def fdel(self):
            pass

        return locals()

    volume = property(**volume())

    def pos():
        def fget(self):
            return pygame.mixer.music.get_pos()

        def fset(self, value):
            if type(value) is int:
                pygame.mixer.music.set_pos(value)

        def fdel(self):
            pass

        return locals()

    pos = property(**pos())
