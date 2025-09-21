import copy as _copy


class widget:
    power = True
    destroyed = False

    def _args(self, locals):
        args = _copy.copy(locals)
        for i in args.items():
            if i[0] != "self":
                exec(f'self.{i[0]} = args["{i[0]}"]')
        self._args = args

    def __init__(self, surface):
        self._args(locals())

    def draw(self, win, pos):
        win.blit(self.surface, pos)

    def on(self):
        self.power = True

    def off(self):
        self.power = False

    def destroy(self):
        self.destroyed = True

    def config(self, **parameters):
        if parameters != {}:
            for i in parameters.items():
                if i[0] in list(self.__dict__.keys()):
                    exec(f'self.{i[0]} = parameters["{i[0]}"]')
                    self._args[i[0]] = i[1]
        else:
            return self._args
        self.__init__(**self._args)


class base:
    def __init__(self, win, bg=(128, 128, 128)):
        self._widgets = {}
        self._bg = bg
        self._win = win
        self._page = 0

    def draw(self):
        self._win.fill(self._bg)
        for i in self._widgets[self._page]:
            if i[0].power:
                i[0].draw(self._win, i[1])
            if i[0].destroyed:
                self._widgets[self._page].remove(i)

    def put(self, widget, pos, page=0):
        if page not in self._widgets:
            self.blankPage(page)
        self._widgets[page].append([widget, pos])

    def selectPage(self, page):
        self._page = page

    def getPage(self):
        return self._page

    def getWidgets(self, page=0):
        return self._widgets[page]

    def setWidgetPos(self, index, pos, page=0):
        self._widgets[page][index] = [self._widgets[page][index][0], pos]

    def blankPage(self, page):
        self._widgets.update({page: []})
