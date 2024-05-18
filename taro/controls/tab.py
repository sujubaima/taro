# -- coding: utf-8 --
import logging

from taro.utils import strutils
from taro.core import UI
from taro.core.event import UIEvent
from taro.controls.canvas import Canvas
from taro.controls.button import Button


LOG = logging.getLogger()


class Tab(Canvas):

    _text = None

    def setup(self, text=None, closable=False):
        super(Tab, self).setup(border=Canvas.BD_STANDARD)
        self.idx = -1
        self.name = None
        self.group = None
        self.closable = closable
        if self.closable:
            self.button_close = Button(text="X", width=3, resizable=False, active=False)
            self.add(self.button_close)
        else:
            self.button_close = None
        if text is not None:
            self.text = text
        if self.closable:
            self.button_close.clicked = lambda evt: self.closed(evt)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, val):
        if self._text == val:
            return
        self._text = val
        width = strutils.strwidth(val)
        if self.closable:
            fullwidth = width + 2 * self.border_x + self.button_close.width + 1
        else:
            fullwidth = width + 2 * self.border_x
        self.resize(width=fullwidth)
        self.flag.modified()

    @property
    def highlight(self):
        return self._highlight

    @highlight.setter
    def highlight(self, val):
        if self._highlight == val:
            return
        self._highlight = val
        if val:
            self.upper()
        self.flag.modified()

    def closed(self, evt):
        tab, canvas = self.group.removetab(self.name)
        tab.destroy()
        canvas.destroy()

    def paint(self):
        if self.group is None:
            return
        super(Tab, self).paint()
        #if self.group.mode == 0:
        #    self.cursor.move(0, 0)
        #    self.cursor.text(self.text)
        #    if self.closable:
        #        self.button_close.locate(pos_x=self.iwidth - self.button_close.width)
        #    self._change_horizontal()
        #else:
        #    self.cursor.move(0, 0)
        #    if self.closable:
        #        self.button_close.locate(pos_x=0)
        #        self.cursor.move(0, self.button_close.width + 2)
        #    self.cursor.text(self.text)
        #    self._change_vertical()
        self.cursor.move(0, 0)
        if self.active:
            self.cursor.text(self.text)
        else:
            self.cursor.text(self.text, fcolor="grey", attrs=["bold"])
        if self.closable:
                self.button_close.locate(pos_x=self.iwidth - self.button_close.width)
        if self.group.mode == 0:
            self._change_horizontal()
        else:
            self._change_vertical()

    def _change_horizontal(self):
        if self.highlight:
            self.cursor.move(1, -1)
            self.cursor.text(" " * (self.iwidth + 2))
            self.cursor.text("└")
            if self != self.group.tabs[0]:
                self.cursor.move(1, -2)
                self.cursor.text("┘")
        else:
            #self.cursor.move(1, -1)
            #self.cursor.text("─" * (self.iwidth + 3))
            #self.cursor.text("─")
            #self.cursor.move(1, -2)
            #self.cursor.text("─")
            self.cursor.move(1, -2)
            self.cursor.text("─" * self.width)

    def _change_vertical(self):
        if self.highlight:
            self.cursor.move(0, self.iwidth + 1)
            self.cursor.text(" ")
            self.cursor.move(1, self.iwidth + 1)
            self.cursor.text("┐")
            if self != self.group.tabs[0]:
                self.cursor.move(-1, self.iwidth + 1)
                self.cursor.text("┘")
        else:
            self.cursor.move(-1, self.iwidth + 1)
            self.cursor.text("│")
            self.cursor.move(0, self.iwidth + 1)
            self.cursor.text("│")
            self.cursor.move(1, self.iwidth + 1)
            self.cursor.text("│")

    def _mouse_left_clicked(self, evt):
        if not self.within(evt.pos_y, evt.pos_x):
            return
        self.group.selected = self

    def _mouse_left_released(self, evt):
        if not self.within(evt.pos_y, evt.pos_x):
            return
        self.group.selected = self


class TabGroup(Canvas):

    class TabChanged(UIEvent):
        pass

    Horizonal = 0
    Vertical = 1

    _selected = None

    def setup(self, mode=0):
        self.mode = mode
        self.tabs = []
        self.canvas = []
        super(TabGroup, self).setup(border=Canvas.BD_STANDARD)
        self._tab_pos_y = -1
        self._tab_pos_x = -2
        self._canvas_pos_y = 2
        self._canvas_pos_x = 8
        self._name_tab = {}
        self._name_canvas = {}
        self.empty = True

        self.handler(TabGroup.TabChanged, "tab_changed")

    @property
    def iwidth(self):
        if self.mode == 0:
            return self.width - 4
        else:
            return self.width - self._canvas_pos_x - 4

    @property
    def iheight(self):
        if self.mode == 0:
            return self.height - 4
        else:
            return self.height - 2

    @property
    def current(self):
        if self.selected is None:
            return None
        else:
            return self.canvas[self.selected.idx]

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
            if oldval.text in self._name_canvas:
                self._name_canvas[oldval.text].off()
            if oldval.closable:
                oldval.button_close.active = False
        if val is not None:
            val.highlight = True
            if val.text in self._name_canvas:
                self._name_canvas[val.text].on()
            if val.closable:
                val.button_close.active = True
        self.event(TabGroup.TabChanged())

    def childsight(self, child):
        if self.mode == TabGroup.Horizonal:
            sight = UI.recinter((self.sight_y, self.sight_x, self.sight_height, self.sight_width),
                                (self.abs_y + self.border_y, self.abs_x + self.border_x,
                                 self.iheight + 2, self.iwidth))
        else:
            sight = UI.recinter((self.sight_y, self.sight_x, self.sight_height, self.sight_width),
                                (self.abs_y + self.border_y, self.abs_x + self.border_x,
                                 self.iheight, self.iwidth + self._canvas_pos_x))
        child.resight(*sight)

    def addtab(self, name, active=True, closable=False): 
        tab = Tab(text=name, closable=closable, height=3, active=active)
        tab.name = name
        self._name_tab[name] = tab
        self.tabs.append(tab)
        if self.mode == TabGroup.Horizonal:
            self.add(tab, pos_y=-1, pos_x=self._tab_pos_x)
            self._tab_pos_x += tab.width - 1
        else:
            if self._canvas_pos_x < tab.width:
                self._canvas_pos_x = tab.width
                for old_tab in self.tabs:
                    old_tab.resize(width=self._canvas_pos_x)
                for canvas in self.canvas:
                    canvas.locate(pos_x=self._canvas_pos_x - 1)
            elif self._canvas_pos_x > tab.width:
                tab.resize(width=self._canvas_pos_x)
            self.add(tab, pos_y=self._tab_pos_y, pos_x=-2)
            self._tab_pos_y += tab.height - 1
        tab.idx = len(self.tabs) - 1
        tab.group = self
        if self.selected is None:
            self.selected = tab
        return tab

    def addcanvas(self, name, canvas, active=True, closable=False):
        canvas.off()
        if name not in self._name_tab:
            self.addtab(name, active=active, closable=closable)
        tab = self._name_tab[name]
        self.canvas.insert(tab.idx, canvas)
        self._name_canvas[name] = canvas
        if self.mode == TabGroup.Horizonal:
            self.add(canvas, pos_y=self._canvas_pos_y)
        else:
            self.add(canvas, pos_x=self._canvas_pos_x - 1)
        if self.selected == tab:
            canvas.on()
        return tab

    def removetab(self, name):
        tab = self._name_tab.get(name, None)
        canvas = self._name_canvas.get(name, None)
        if tab is not None:
            self.tabs.remove(tab)
            self._name_tab.pop(name)
        if canvas is not None:
            self.canvas.remove(canvas)
            self._name_canvas.pop(name)
        if tab is None:
            return tab, canvas
        if self.mode == TabGroup.Horizonal:
            self._tab_pos_x -= tab.width - 1
            for old_tab in self.tabs:
                if old_tab.idx > tab.idx:
                    old_tab.idx -= 1
                    old_tab.locate(pos_x=old_tab.pos_x - tab.width + 1)
        else:
            self._canvas_pos_x = 8
            for old_tab in self.tabs:
                self._canvas_pos_x = max(old_tab.width, self._canvas_pos_x)
            for old_tab in self.tabs:
                old_tab.resize(width=self._canvas_pos_x)
                if old_tab.idx > tab.idx:
                    old_tab.idx -= 1
                    old_tab.locate(pos_y=old_tab.pos_y - tab.height + 1)
            for old_canvas in self.canvas:
                old_canvas.locate(pos_x=self._canvas_pos_x - 1)
            self._tab_pos_y -= tab.height - 1
        if len(self.tabs) > 0:
            self.selected = self.tabs[min(tab.idx, len(self.tabs) - 1)]
        else:
            self.selected = None
        return tab, canvas

    def paint(self):
        super(TabGroup, self).paint()
        #self.cursor.move(-1, -2)
        #self.cursor.text("╭")
        #if self.empty:
        #    self.addtab("")
        if self.mode == TabGroup.Horizonal:
            self._paint_horizonal()
        else:
            self._paint_vertical()

    def _paint_horizonal(self):
        self.cursor.move(-1, self._tab_pos_x + 1)
        #self.cursor.text("┐")
        self.cursor.text(" " * (self.iwidth - self._tab_pos_x + 1))
        self.cursor.move(0, self.iwidth + 1)
        self.cursor.text(" ")
        if len(self.tabs) > 0:
            if self.selected != self.tabs[0]:
                self.cursor.move(1, -2)
                self.cursor.text("├─")
            else:
                self.cursor.move(1, -2)
                self.cursor.text("│ ")
            self.cursor.move(1, self._tab_pos_x)
            self.cursor.text("─" * (self.iwidth - self._tab_pos_x + 1))
            self.cursor.text("┐")
            for idx, tab in enumerate(self.tabs):
                #if tab == self.selected and idx != 0:
                #    self.cursor.move(tab.pos_y, tab.pos_x)
                #    #self.cursor.text("┌")
                #    self.cursor.text("╭")
                self.cursor.move(tab.pos_y, tab.pos_x + tab.width - 1)
                #self.cursor.text("┐")
                self.cursor.text("╮")
        else:
            self.cursor.move(1, -2)
            self.cursor.text("│ ")
            self.cursor.move(-1, -1)
            self.cursor.text("──╮")
            self.cursor.move(0, 1)
            self.cursor.text("│")
            self.cursor.move(1, 1)
            self.cursor.text("└")
            self.cursor.text("─" * (self.iwidth - 2 + 1))
            self.cursor.text("┐")


    def _paint_vertical(self):
        self.cursor.move(self._tab_pos_y, -2)
        while self.cursor.pos_y != self.height - 2:
            self.cursor.move(self.cursor.pos_y + 1, -2)
            self.cursor.text("  ")
        self.cursor.move(self.iheight, -2)
        self.cursor.text(" " * self._canvas_pos_x)
        if len(self.tabs) > 0:
            if self.selected != self.tabs[0]:
                self.cursor.move(-1, self._canvas_pos_x - 3)
                self.cursor.text("┬")
            else:
                self.cursor.move(-1, self._canvas_pos_x - 3)
                self.cursor.text("─")
            self.cursor.move(1, self._tab_pos_x)
            self.cursor.move(self._tab_pos_y, self._canvas_pos_x - 3)
            while self.cursor.pos_y != self.height - 3:
                self.cursor.move(self.cursor.pos_y + 1, self._canvas_pos_x - 3)
                self.cursor.text("│")
            self.cursor.move(self.cursor.pos_y + 1, self._canvas_pos_x - 3)
            self.cursor.text("└")
            for idx, tab in enumerate(self.tabs):
                #if tab == self.selected and idx != 0:
                #    self.cursor.move(tab.pos_y, tab.pos_x)
                #    #self.cursor.text("┌")
                #    self.cursor.text("╭─")
                self.cursor.move(tab.pos_y + tab.height - 1, tab.pos_x)
                #self.cursor.text("┐")
                self.cursor.text("╰─")
        else:
            self.cursor.move(0, -2)
            self.cursor.text("╰─")
            self.cursor.text("─" * (self._canvas_pos_x - 3))
            self.cursor.text("┐")
            while self.cursor.pos_y != self.height - 3:
                self.cursor.move(self.cursor.pos_y + 1, self._canvas_pos_x - 3)
                self.cursor.text("│ ")
            self.cursor.move(self.cursor.pos_y + 1, self._canvas_pos_x - 3)
            self.cursor.text("└")

