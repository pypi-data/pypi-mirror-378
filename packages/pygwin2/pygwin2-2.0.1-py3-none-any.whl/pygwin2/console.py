from . import pygame

try:
    import win32console
    import win32con
    import win32gui

    nonwin = False
except Exception as _:
    nonwin = True
import pyautogui


class console:
    def __init__(self):
        if not nonwin:
            self._hwnd = win32console.GetConsoleWindow()

    @property
    def hwnd(self):
        if not nonwin:
            return self._hwnd

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
            win32gui.SetWindowPos(self.hwnd, x, y, self.size[0], self.size[1])

    def resize(self, width, height):
        if not nonwin:
            win32gui.SetWindowPos(
                self.hwnd, self.position[0], self.position[1], width, height
            )

    def minimize(self):
        if not nonwin:
            win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)
            return self.size

    def maximize(self):
        if not nonwin:
            win32gui.ShowWindow(self.hwnd, win32con.SW_MAXIMIZE)
            return self.size

    def title():
        def fget(self):
            if not nonwin:
                return win32console.GetConsoleTitle()

        def fset(self, value):
            if not nonwin:
                win32console.SetConsoleTitle(str(value))

        def fdel(self):
            pass

        return locals()

    title = property(**title())

    def center(
        self,
        x=pygame.display.get_desktop_sizes()[0][0] / 2,
        y=pygame.display.get_desktop_sizes()[0][1] / 2,
    ):
        if not nonwin:
            self.move(x - self.size[0] / 2, y - self.size[1] / 2)

    @property
    def visible(self):
        if not nonwin:
            return win32gui.IsWindowVisible(self.hwnd)

    @property
    def position(self):
        if not nonwin:
            rect = win32gui.GetWindowRect(self.hwnd)
            x = rect[0] + 7
            y = rect[1]
            return (x, y)

    @property
    def size(self):
        if not nonwin:
            rect = win32gui.GetWindowRect(self.hwnd)
            w = rect[2] - self.position[0] - 7
            h = rect[3] - self.position[1] - 7
            return (w, h)

    def screenshot(self, path):
        if not nonwin:
            rect = self.position + self.size
            self.focus()
            pyautogui.screenshot(path, region=rect)
            return path


console = console()
