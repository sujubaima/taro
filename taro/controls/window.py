# -- coding: utf-8 --
import os
import time
import threading
import curses
import logging

from taro.utils import strutils
from taro.core import UI
from taro.controls.canvas import Canvas
from taro.controls.button import Button


LOG = logging.getLogger()


class Window(Canvas):

    #width = 44
    #height = 12

    _title = "NewWindow"

    #_title_repaint = True

    _height_title = 2

    _mouse_y = 0
    _mouse_x = 0

    _pressed = False
 
    def setup(self, zindex=1, title=None, draggable=True):

        self.zindex = zindex
        self.highlight = True

        super(Window, self).setup(title=title, border=Canvas.BD_STANDARD, shadow=False)

        self.closer = Button(text="X", width=3, resizable=False)
        self.add(self.closer, pos_y=-2, pos_x=self.iwidth - self.closer.width)

        #self._pressed = False
        #self._mouse_y = 0
        #self._mouse_x = 0

        self.draggable = draggable

        #if title is not None:
        #    self.title = title

        self.closed = lambda evt: None
        self.closer.clicked = lambda evt: self.closed(evt)

        self.abs_y_ = self.abs_y
        self.abs_x_ = self.abs_x

    @property
    def iheight(self):
        return self.height - 2 * self.border_y - self._height_title

    def coordinate(self):
        if self.parent is not None:
            self.coord_x = self.parent.coord_x + self.parent.pos_x
            self.coord_y = self.parent.coord_y + self.parent.pos_y
        self.abs_x = self.coord_x + self.pos_x
        self.abs_y = self.coord_y + self.pos_y
        self.coord_y += self.border_y
        self.coord_x += self.border_x
        #self.closer.coordinate()
        self.coord_y += self._height_title
        for child in self.children:
            #if child == self.closer:
            #    continue
            child.coordinate()

    def locate(self, pos_y=None, pos_x=None):
        super(Window, self).locate(pos_y=pos_y, pos_x=pos_x)
        UI.Root.flag.modified()

    def childsight(self, child):
        sight = UI.recinter((self.sight_y, self.sight_x, self.sight_height, self.sight_width),
                            (self.abs_y + self.border_y, self.abs_x + self.border_x,
                             self.iheight + 2, self.iwidth))
        child.resight(*sight)

    def _size_changed(self):
        self.sub_height = self.height - 2 * self.border_y - self._height_title
        self.sub_width = self.width - 2 * self.border_x
        self._update_sight()
        for child in self.children:
            if child.fixed:
                continue
            child.resize(self.sub_height, self.sub_width)
        if self.view is not None:
            self.view.resize(self.sub_height, self.sub_width)

    #def paint(self):
    #    #self.cursor.reset()
    #    #if self._title_repaint:
    #    self._paint_title()
    #    #self._shades()
    #    super(Window, self).paint()

    def _paint_title(self):
        self.cursor.move(0, -1)
        if self.highlight:
            self.cursor.text(strutils.align_left(" " + self.title, self.iwidth - 2), bcolor="blue", attrs=["bold"])
            self.cursor.move(0, self.iwidth)
            self.cursor.textline(" ", bcolor="blue")
        else:
            self.cursor.text(strutils.align_left(" " + self.title, self.iwidth - 2), attrs=["bold"])
            self.cursor.move(0, self.iwidth)
            self.cursor.textline(" ")
        self.cursor.textline("-" * (self.width - 2 * self.border_x), attrs=["bold"])
        #self._title_repaint = False
        self.closer.flag.modified()
        #self.closer.locate(pos_x=10)

    def within_title(self, pos_y, pos_x):
        if pos_y < self.abs_y or pos_y > self.abs_y + 2:
            return False
        if pos_x <= self.abs_x or pos_x >= self.abs_x + self.iwidth - 1:
            return False
        for ctrl in self.parent.children:
            if ctrl == self or not ctrl.active:
                continue
            if ctrl.zindex >= self.zindex and ctrl.within(pos_y, pos_x):
                return False
        return True

    def upper(self):
        super(Window, self).upper()
        for child in self.parent.children:
            if child != self:
                child.highlight = False
        self.highlight = True

    def _mouse_left_clicked(self, evt):
        if not self.within_title(evt.pos_y, evt.pos_x):
            return
        self.upper()

    def _mouse_left_double_clicked(self, evt):
        if not self.within_title(evt.pos_y, evt.pos_x):
            return
        self.upper()

    def _mouse_left_pressed(self, evt):
        if not self.within_title(evt.pos_y, evt.pos_x):
            return
        self.upper()
        if not self.draggable:
            return
        if self._pressed:
            return
        self._pressed = True
        self._mouse_y = evt.pos_y
        self._mouse_x = evt.pos_x

    def _mouse_left_released(self, evt):
        if not self.draggable:
            return
        if not self._pressed:
            return 
        self._pressed = False
        offset_y = evt.pos_y - self._mouse_y
        offset_x = evt.pos_x - self._mouse_x
        offset_y = min(max(offset_y, 0 - self.abs_y), UI.ScreenHeight - self.abs_y - self.height)
        offset_x = min(max(offset_x, 0 - self.abs_x), UI.ScreenWidth - self.abs_x - self.width)
        #self.move(offset_y, offset_x)
        self.pos_y_ = self.pos_y + offset_y
        self.pos_x_ = self.pos_x + offset_x
        self._mouse_y = evt.pos_y
        self._mouse_x = evt.pos_x
        self._pressed = False
        self._move_window()

    def _move_window(self):
        if self.pos_y == self.pos_y_ and self.pos_x == self.pos_x_:
            return
        pos_y, pos_x = self.pos_y, self.pos_x
        if self.pos_y > self.pos_y_:
            pos_y = max(self.pos_y_, pos_y - 6)
        elif self.pos_y < self.pos_y_:
            pos_y = min(self.pos_y_, pos_y + 6)
        if self.pos_x > self.pos_x_:
            pos_x = max(self.pos_x_, pos_x - 12)
        elif self.pos_x < self.pos_x_:
            pos_x = min(self.pos_x_, pos_x + 12)
        self.locate(pos_y, pos_x)
        timer = threading.Timer(0.05, self._move_window)
        timer.start()
        
