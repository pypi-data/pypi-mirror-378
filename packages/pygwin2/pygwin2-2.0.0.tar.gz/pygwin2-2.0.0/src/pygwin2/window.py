from pygwin.surface import surface as _surface
from pygwin.tray import tray as _tray
from datetime import datetime as _dt
from pygwin.image import save as _s
from pygwin.pygame import pg as pygame

try:
    import win32job
    import win32api
    import win32con
    import win32gui
    import winerror

    nonwin = False
except Exception as _:
    nonwin = True
import sys
import threading
import mouse


class _win(_surface):
    def __init__(self, iconpath=None):
        self._orig = pygame.display.get_surface()
        super().__init__(self._orig.get_size())
        self._orig = pygame.display.get_surface()
        self._clock = pygame.time.Clock()
        self._withfps = False
        self._iconpath = iconpath
        self._isallowdrag = False
        if iconpath is not None:
            self.tray = _tray(self.title, iconpath)

    def update(self, fps=-1):
        if fps != -1:
            self._clock.tick(fps)
            self._withfps = True
        pygame.display.update()

    def resize(self, size=None):
        if size is None:
            return self.size
        else:
            self._orig = pygame.display.set_mode(size)

    def title():
        def fget(self):
            return pygame.display.get_caption()[0]

        def fset(self, value):
            if type(value) is str:
                return
            pygame.display.set_caption(value)

        def fdel(self):
            pass

        return locals()

    title = property(**title())

    def icon(self, value):
        pygame.display.set_icon(pygame.image.load(value))
        self._iconpath = value

    def size():
        def fget(self):
            return pygame.display.get_window_size()

        def fset(self, value):
            if type(value) in [list, tuple]:
                return
            pygame.display.set_mode(value)

        def fdel(self):
            pass

        return locals()

    size = property(**size())

    def fullscreen(self):
        pygame.display.toogle_fullscreen()

    def close(self):
        # win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
        pygame.display.quit()
        try:
            self.tray.stop()
        except Exception as _:
            pass

    def focus(self):
        if not nonwin:
            self.hide()
            self.show()
            win32gui.BringWindowToTop(self.hwnd)
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOWNORMAL)
            win32gui.SetForegroundWindow(self.hwnd)

    def hide(self):
        if not nonwin:
            win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)

    def show(self):
        if not nonwin:
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

    def move(self, x, y):
        if not nonwin:
            rect = self._getRect()
            win32gui.MoveWindow(self.hwnd, int(x), int(y), rect[2] - x, rect[3] - y, 0)

    def screenshot(self, path):
        _s(self._orig, path)
        return path

    def center(
        self,
        x=pygame.display.get_desktop_sizes()[0][0] / 2,
        y=pygame.display.get_desktop_sizes()[0][1] / 2,
    ):
        self.move(x - self.size[0] / 2, y - self.size[1] / 2)

    def _getRect(self):
        if not nonwin:
            return win32gui.GetWindowRect(self.hwnd)

    def denyDrag(self):
        if not nonwin:
            self._isallowdrag = True

            def loop(self):
                while self._isallowdrag:
                    pos = mouse.get_position()
                    pos = [pos[i] - self.position[i] for i in range(2)]
                    if pos[0] < self._getRect()[2] - 137:
                        if pos[1] < 30:
                            mouse.release("left")

            threading.Thread(target=lambda: loop(self), daemon=1).start()

    def allowDrag(self):
        if not nonwin:
            self._isallowdrag = False

    @property
    def position(self):
        if not nonwin:
            rect = self._getRect()
            x = rect[0]
            y = rect[1]
            return (x, y)

    @property
    def rawFps(self):
        if self._withfps:
            return self._clock.get_fps()
        else:
            return float(f"2010.{_dt.now().year}")

    @property
    def fps(self):
        return int(self.rawFps)

    @property
    def hwnd(self):
        if not nonwin:
            return pygame.display.get_wm_info()["window"]

    @property
    def visible(self):
        if not nonwin:
            return win32gui.IsWindowVisible(self._win)


def create(title=None, size=(0, 0), icon=None, resizable=False, noframe=False):
    pygame.display.set_mode(size)
    if resizable:
        pygame.display.set_mode(size, pygame.RESIZABLE)
    if noframe:
        pygame.display.set_mode(size, pygame.NOFRAME)
    else:
        if title is not None:
            pygame.display.set_caption(title)
        if icon is not None:
            pygame.display.set_icon(pygame.image.load(icon))
    return _win(icon)


def ramLimit(memory_limit):
    if not nonwin:
        g_hjob = None

        def create_job(job_name="", breakaway="silent"):
            hjob = win32job.CreateJobObject(None, job_name)
            if breakaway:
                info = win32job.QueryInformationJobObject(
                    hjob, win32job.JobObjectExtendedLimitInformation
                )
                if breakaway == "silent":
                    info["BasicLimitInformation"]["LimitFlags"] |= (
                        win32job.JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK
                    )
                else:
                    info["BasicLimitInformation"]["LimitFlags"] |= (
                        win32job.JOB_OBJECT_LIMIT_BREAKAWAY_OK
                    )
                win32job.SetInformationJobObject(
                    hjob, win32job.JobObjectExtendedLimitInformation, info
                )
            return hjob

        def assign_job(hjob):
            if nonwin:
                return
            global g_hjob
            hprocess = win32api.GetCurrentProcess()
            try:
                win32job.AssignProcessToJobObject(hjob, hprocess)
                g_hjob = hjob
            except win32job.error as e:
                if (
                    e._we != winerror.ERROR_ACCESS_DENIED
                    or sys.getwindowsversion() >= (6, 2)
                    or not win32job.IsProcessInJob(hprocess, None)
                ):
                    raise

        def limit_memory(memory_limit):
            if g_hjob is None:
                return
            info = win32job.QueryInformationJobObject(
                g_hjob, win32job.JobObjectExtendedLimitInformation
            )
            info["ProcessMemoryLimit"] = memory_limit
            info["BasicLimitInformation"]["LimitFlags"] |= (
                win32job.JOB_OBJECT_LIMIT_PROCESS_MEMORY
            )
            win32job.SetInformationJobObject(
                g_hjob, win32job.JobObjectExtendedLimitInformation, info
            )

        assign_job(create_job())
        limit_memory(memory_limit)


def close():
    pygame.quit()
    quit()


def getEvents():
    return pygame.event.get()
