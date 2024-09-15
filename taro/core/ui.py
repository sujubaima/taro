# -- coding: utf-8 --
import os
import re
import sys
import traceback
import platform
import time
import struct
import queue
import threading
import logging

import curses
import curses.ascii

from taro import options
from taro.utils.strutils import Colored
from taro.utils.strutils import strwidth
from taro.utils.strutils import unicoded
from taro.utils import log

from taro.core.event import *
from taro.core.cursor import UICursor


LOG = logging.getLogger()


class UI(object):
    """
    所有UI控件的基类，包括以下主要基本属性
    pos_y, pos_x: 相对父控件的坐标
    abs_y, abs_x: 相对屏幕的绝对坐标
    height, width: 控件完整绘制的高度与宽度
    sight_y, sight_x: 控件可见区域相对屏幕的绝对坐标
    sight_height, sight_width: 控件可见区域的高度与宽度

    parent: 当前控件的父控件
    children: 当前控件的子控件，其绝对位置与可见区域会受到当前控件的影响
    """
    All = {}

    id_ = -1

    Root = None

    ScreenHeight = -1
    ScreenWidth = -1

    Focused = None

    pos_x = 0
    pos_y = 0
    width = 1
    height = 1

    Modified = 2 << 1
    Moved = 2 << 2
    Resized = 2 << 3
    Redrawed = 2 << 4
    Erased = 2 << 5

    _visible = False
    _active = False
    _highlight = False

    _zindex = 0

    _stack = []


    class UIFlag(object):

        def __init__(self):
            self._flag = UI.Modified
            self._recs = []
            self._lock = threading.Lock()

        def modified(self, *recs):
            with self._lock:
                self._flag |= UI.Modified
                if len(recs) > 0:
                    self._recs.extend(recs)

        def moved(self):
            with self._lock:
                self._flag |= UI.Moved

        def resized(self):
            with self._lock:
                self._flag |= UI.Resized

        def redrawed(self):
            with self._lock:
                self._flag |= UI.Redrawed

        def erased(self):
            with self._lock:
                self._flag |= UI.Erased

        def reset(self):
            with self._lock:
                self._flag = 0
                self._recs.clear()


    def __init__(self, id=None, height=None, width=None, new_cursor=True, 
                 resizable=True, visible=True, active=True, autofresh=False, **kwargs):

        # 递增ID
        if id is None:
            UI.id_ += 1
            self.id = UI.id_
        else:
            self.id = id

        UI.All[self.id] = self

        self.resizable = resizable

        self.fixed = True

        if width is not None:
            self.width = width
        if height is not None:
            self.height = height

        self.coord_x = 0
        self.coord_y = 0

        self.abs_x = self.pos_x
        self.abs_y = self.pos_y

        self.sight_x = 0
        self.sight_y = 0
        self.sight_width = curses.COLS
        self.sight_height = curses.LINES

        self.flag = UI.UIFlag()

        self.parent = None
        self.children = []
        self.binddata = None

        self.handlers = {}
        self.handler(MouseLeftClicked, "_mouse_left_clicked")
        self.handler(MouseLeftDoubleClicked, "_mouse_left_double_clicked")
        self.handler(MouseLeftPressed, "_mouse_left_pressed")
        self.handler(MouseLeftReleased, "_mouse_left_released")
        self.handler(MouseRightClicked, "_mouse_right_clicked")
        self.handler(MouseRightDoubleClicked, "_mouse_right_double_clicked")
        self.handler(MouseRightPressed, "_mouse_right_pressed")
        self.handler(MouseRightReleased, "_mouse_right_released")
        self.handler(MouseScrollUp, "_mouse_scroll_up")
        self.handler(MouseScrollDown, "_mouse_scroll_down")
        self.handler(MouseMove, "_mouse_moved")
        self.handler(KeyInput, "_key_input")

        self.cursor = None
        self._alock = threading.Lock()
        self._ancestor = None
        self._new_cursor = new_cursor
        self.autofresh = False

        self.setup(**kwargs)
        
        if UI.Root is not None and self.parent is None:
            #self.parent = UI.Root
            #UI.Root.children.append(self)
            UI.Root.add(self)

        self.autofresh = autofresh
        #self._active = active
        self._visible = visible
        self._active = active

    def __hash__(self):
        return hash(self.id)

    def setup(self, **kwargs):
        if self._new_cursor:
            cswin_ = curses.newpad(self.height, self.width)
            cswin_.keypad(1)
            self.cursor = UICursor(cswin_)
            self.ancestor = self
            
    @property
    def iheight(self):
        return self.height

    @property
    def iwidth(self):
        return self.width

    @property
    def ancestor(self):
        return self._ancestor

    @ancestor.setter
    def ancestor(self, val):
        with self._alock:
            self._ancestor = val

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, val):
        if self._visible == val:
            return
        self._visible = val
        if not val:
            #self.cswin_.erase()
            UI.Root.flag.redrawed()
        UI.Root.flag.modified()

    @property
    def zindex(self):
        return self._zindex

    @zindex.setter
    def zindex(self, val):
        if self._zindex == val:
            return
        self._zindex = val
        if self.parent is not None:
            self.parent.children.sort(key=lambda x: x.zindex)
        self.flag.moved()

    @property
    def uppermost(self):
        return max([child.zindex for child in self.children])

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, val):
        if self._active == val:
            return
        self._active = val
        UI.Root.flag.modified()
        #for child in self.children:
        #    child.active = val

    @property
    def highlight(self):
        return self._highlight

    @highlight.setter
    def highlight(self, highlight):
        if self._highlight == highlight:
            return
        self._highlight = highlight
        self.flag.modified()

    def to_abs(self, pos_y, pos_x):
        return (self.abs_y + pos_y, self.abs_x + pos_x)

    def to_pos(self, abs_y, abs_x):
        return (abs_y - self.abs_y, abs_x - self.abs_x)

    def canseen(self):
        if self.sight_height <= 0 or self.sight_width <= 0:
            return False
        if self.abs_y >= self.sight_y + self.sight_height or \
           self.abs_x >= self.sight_x + self.sight_width or \
           self.abs_y + self.height <= self.sight_y or \
           self.abs_x + self.width <= self.sight_x:
            return False
        return True

    def within(self, abs_y, abs_x):
        if abs_y < self.abs_y or abs_y >= self.abs_y + self.height:
            return False
        if abs_x < self.abs_x or abs_x >= self.abs_x + self.width:
            return False
        return True

    def on(self):
        self.visible = True
        self.active = True

    def off(self):
        self.visible = False
        self.active = False

    def resize(self, height=None, width=None):
        if not self.resizable:
            return
        if height is None:
            height = self.height
        if width is None:
            width = self.width
        if height == self.height and width == self.width:
            return
        self.height = height
        self.width = width
        if self.cursor is not None:
            self.cursor.cswin_.resize(self.height, self.width)
        if self.parent is not None:
            self.parent.childsight(self)
        self.size_changed()
        self.flag.resized()

    def locate(self, pos_y=None, pos_x=None):
        if pos_y is None:
            pos_y = self.pos_y
        if pos_x is None:
            pos_x = self.pos_x
        if pos_y == self.pos_y and pos_x == self.pos_x:
            return
        self.pos_y = pos_y
        self.pos_x = pos_x
        self.coordinate()
        if self.parent is not None:
            self.parent.childsight(self)
        #self.location_changed()
        self.flag.moved()
        #self.flag |= UI.Modified

    def move(self, offset_y=0, offset_x=0):
        self.locate(self.pos_y + offset_y, self.pos_x + offset_x)

    #def resize(self, height=None, width=None):
    #    if height is None:
    #        height = self.height
    #    if width is None:
    #        width = self.width
    #    if height == self.height and width == self.width:
    #        return
    #    self.height = height
    #    self.width = width
    #    if self.parent is not None:
    #        self.parent.resight()
    #    self.size_changed()
    #    self.flag |= UI.Resized

    #def location_changed(self):
    #    self.resight()

    def size_changed(self):
        pass

    def coordinate(self):
        if self.parent is not None:
            self.coord_x = self.parent.coord_x + self.parent.pos_x
            self.coord_y = self.parent.coord_y + self.parent.pos_y
        self.abs_x = self.coord_x + self.pos_x
        self.abs_y = self.coord_y + self.pos_y
        for child in self.children:
            child.coordinate()

    def resight(self, sight_y=None, sight_x=None, height=None, width=None):
        if sight_y is not None:
            self.sight_y = sight_y
        if sight_x is not None:
            self.sight_x = sight_x
        if height is not None:
            self.sight_height = height
        if width is not None:
            self.sight_width = width
        for child in self.children:
            self.childsight(child)
            #child.resight(self.sight_y, self.sight_x, self.sight_height, self.sight_width)

    def childsight(self, child):
        sight = UI.recinter((self.sight_y, self.sight_x, self.sight_height, self.sight_width),
                            (self.abs_y, self.abs_x, self.height, self.width))
        child.resight(*sight)

    def add(self, child, *args, **kwargs):
        if child.parent is not None:
            child.parent.remove(child)
        if child.ancestor == None:
            child.ancestor = self.ancestor
        child.parent = self
        self.children.append(child)
        #    child.cursor = self.cursor.clone()
        #    child.cursor.start_y = self.cursor.start_y + child.pos_y
        #    child.cursor.start_x = self.cursor.start_x + child.pos_x
        self.children.sort(key=lambda x: x.zindex)
        #child.zindex = self.uppermost + 1
        #child.coordinate()
        #self.add_hook(child)
        self.coordinate()
        self.resight()

    def remove(self, child, *args, **kwargs):
        self.children.remove(child)
        child.parent = None
        if child.ancestor != child:
            child.ancestor = None

    def rendering(self):
        if self.autofresh:
            self.flag.modified()
            self.cursor.reset()

    def rendered(self):
        pass

    def paint(self, *recs):
        pass

    def update(self):
        pass

    def _vision_scope(self):
        if self.ancestor == self:
            start_y = max(0, self.sight_y - self.abs_y)
            start_x = max(0, self.sight_x - self.abs_x)
        else:
            start_y = max(self.abs_y - self.ancestor.abs_y, self.sight_y - self.abs_y)
            start_x = max(self.abs_x - self.ancestor.abs_x, self.sight_x - self.abs_x)
        pos_y = max(self.abs_y, self.sight_y)
        pos_x = max(self.abs_x, self.sight_x)
        end_y = min(self.abs_y + self.height - 1, self.sight_y + self.sight_height - 1)
        end_x = min(self.abs_x + self.width - 1, self.sight_x + self.sight_width - 1)
        return (start_y, start_x, pos_y, pos_x, end_y, end_x)

    def vision_scope(self):
        tmp_y, tmp_x = self.to_pos(self.abs_y, self.abs_x)
        return (tmp_y, tmp_x, self.height, self.width)

    def _refresh_recs(self):
        if len(self.flag._recs) == 0:
            recs = [self.vision_scope()]
        else:
            recs = self.flag._recs
        for rec in recs:
            abs_y, abs_x = self.to_abs(rec[0], rec[1]) 
            height = rec[2]
            width = rec[3]
            with self._alock:
                if self.ancestor == self:
                    start_y = max(abs_y - self.abs_y, self.sight_y - abs_y)
                    start_x = max(abs_x - self.abs_x, self.sight_x - abs_x)
                else:
                    start_y = max(abs_y - self.ancestor.abs_y, self.sight_y - abs_y)
                    start_x = max(abs_x - self.ancestor.abs_x, self.sight_x - abs_x)
            pos_y = max(abs_y, self.sight_y)
            pos_x = max(abs_x, self.sight_x)
            end_y = min(abs_y + height - 1, self.sight_y + self.sight_height - 1)
            end_x = min(abs_x + width - 1, self.sight_x + self.sight_width - 1)
            yield (start_y, start_x, pos_y, pos_x, end_y, end_x)

    def _refresh(self):
        try:
            for rec in self._refresh_recs():
                self.cursor.cswin_.noutrefresh(*rec)
            #self.cursor.cswin_.noutrefresh(*self._vision_scope())
        except Exception as e:
            #LOG.error("Refresh %s error: start(%s, %s), abs(%s, %s), end(%s, %s)" % \
            #            (self, *rec))
            #LOG.error("Control: abs(%s, %s), size(%s, %s)" % \
            #            (self.abs_y, self.abs_x, self.height, self.width))
            #LOG.error("Sight: abs(%s, %s), size(%s, %s)" % \
            #            (self.sight_y, self.sight_x, self.sight_height, self.sight_width))
            raise e
        return True

    def refresh(self):
        self.rendering()
        if not self.visible:
            return
        if not self.canseen():
            return
        if self.id not in UI.All:
            UI.All[self.id] = self
        #if self.flag != 0:
        if self.flag._flag != 0:
            with self.flag._lock:
                if self.flag._flag & UI.Modified:
                    self.paint(*self.flag._recs)
                if self.flag._flag & UI.Redrawed:
                    self.cursor.cswin_.redrawwin()
                    self.flag._flag &= ~UI.Redrawed
                #else:
                if self.cursor is not None:
                    self._refresh()
                for child in self.children:
                    child.flag._flag |= self.flag._flag
                self.flag._flag = 0
                self.flag._recs.clear()
        for child in self.children: #sorted(self.children, key=lambda x: x.zindex):
            child.refresh()
        self.rendered()

    def render(self):
        self.refresh()
        curses.doupdate()

    @staticmethod
    def recinter(rec_a, rec_b):
        y = max(rec_a[0], rec_b[0])
        x = max(rec_a[1], rec_b[1])
        height = min(rec_a[0] + rec_a[2], rec_b[0] + rec_b[2]) - y
        width = min(rec_a[1] + rec_a[3], rec_b[1] + rec_b[3]) - x
        return (y, x, height, width)

    @staticmethod
    def renderall():
        UI.Root.refresh()
        curses.doupdate()

    def event(self, evt, glob=False):
        if evt.object is None:
            evt.object = self
        evt.glob = glob
        UIEvent.Queue.put(evt)

    def handle(self, evt):
        if evt.__class__ in self.handlers:
            #func = getattr(self, self.handlers[evt.__class__], None)
            #if func is not None:
            #    func(evt)
            self.handlers[evt.__class__](evt)

    def handler(self, cls, funcname):
        if getattr(self, funcname, None) is None:
            setattr(self, funcname, lambda evt: None)
        self.handlers[cls] = lambda evt: getattr(self, funcname)(evt)

    def destroy(self):
        self.off()
        if self.parent is not None:
            self.parent.remove(self)
        for child in self.children:
            child.destroy()
        if self.cursor is not None:
            del self.cursor.cswin_
            del self.cursor
            self.cursor = None
        UI.All.pop(self.id)

    @staticmethod
    def _(id):
        return UI.All[id]
