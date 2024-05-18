import time

from taro import options

from taro.controls.canvas import Canvas
from taro.controls.button import Button


class MenuItem(Button):

    def setup(self, text, menu):
        super(MenuItem, self).setup(text)
        self.menu = menu


class Menu(Canvas):

    _selected = None

    Right = 0
    Down = 1
    Left = 2
    Up = 3

    def setup(self, popup=0, fixed=False):
        self.items = []
        self.selected = None
        self.pmenu = None
        self.submenus = {}
        self.popup = popup
        super(Menu, self).setup(border=Canvas.BD_STANDARD, fixed=fixed)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, val):
        if self._selected == val:
            return
        oldval = self._selected
        self._selected = val
        if oldval is not None:
            oldval.highlight = False
        if val is not None:
            val.highlight = True

    def additem(self, item, binddata=None, submenu=None):
        item = MenuItem(text=item, menu=self)
        item.binddata = binddata
        super(Menu, self).add(item)
        self.items.append(item)
        if submenu is not None:
            self.submenu(item, submenu)
        return item

    def removeitem(self, item):
        if self.selected == item:
            self.submenus[self.selected].shrink()
        if item in self.submenus:
            self.submenus.pop(item)
        self.layout.remove(item)
        self.items.remove(item)

    def clearitems(self):
        while len(self.items) > 0:
            self.removeitem(self.items[0])

    def submenu(self, item, submenu):
        self.submenus[item] = submenu
        submenu.pmenu = self

    def expand(self, item):
        if self.selected is not None and self.selected != item:
            self.submenus[self.selected].shrink()
        elif self.selected == item:
            self.selected.highlight = True
        self.selected = item
        submenu = self.submenus[self.selected]
        submenu.upper()
        submenu.locate(*self._subpos(item))
        submenu.on()

    def shrink(self):
        if self.selected is not None:
            self.submenus[self.selected].shrink()
        self.off()
        if self.pmenu is not None:
            self.pmenu.selected = None

    def _subpos(self, item):
        if self.popup == Menu.Right:
            return item.abs_y, item.abs_x + item.width
        elif self.popup == Menu.Left:
            return item.abs_y, item.abs_x - item.width
        return 0, 0


#class VerticalMenu(Menu):
#
#    def setup(self):
#        super(VerticalMenu, self).setup()
#        self.layout = LinearLayout(filled=True)
#
#    def _subpos(self, item):
#        return item.abs_y, item.abs_x + item.width
