# -- coding: utf-8 --
import time
import math
import curses
import threading
import logging

from taro import options
from taro.core import UI
from taro.core import UIEvent
from taro.controls.canvas import Canvas


LOG = logging.getLogger()

ARROW_UP = "▲"
ARROW_DOWN = "▼"
ARROW_LEFT = "◀ "
ARROW_RIGHT = " ▶"

BAR_HORIZON = "■"
BAR_VERTICAL = "█"

LINE_HORIZON = "─"
LINE_VERTICAL = "│"


class Scroll(UI):
    """
    滚动条基类
    """
    _offset = 0

    _arrow_clicking = False
    _arrow_released = True

    _arrow_one_highlight = False
    _arrow_two_highlight = False

    arrow_one_pos = None
    arrow_two_pos = None

    offset_step = 1

    min_offset = 0
    max_offset = 1

    class ScrolledEvent(UIEvent):

        def __init__(self, delta):
            super(Scroll.ScrolledEvent, self).__init__()
            self.delta = delta

    def setup(self):
        super(Scroll, self).setup()
        self.handler(Scroll.ScrolledEvent, "scrolled")

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, offset):
        offset = max(offset, self.min_offset) 
        offset = min(offset, self.max_offset)
        if offset == self._offset:
            return
        delta = offset - self._offset
        self._offset = offset
        self.flag.modified()
        self.event(Scroll.ScrolledEvent(delta))

    @property
    def arrow_one_highlight(self):
        return self._arrow_one_highlight

    @arrow_one_highlight.setter
    def arrow_one_highlight(self, val):
        if self._arrow_one_highlight == val:
            return
        self._arrow_one_highlight = val
        self.flag.modified()

    @property
    def arrow_two_highlight(self):
        return self._arrow_two_highlight

    @arrow_two_highlight.setter
    def arrow_two_highlight(self, val):
        if self._arrow_two_highlight == val:
            return
        self._arrow_two_highlight = val
        self.flag.modified()

    def within_arrow(self, evt):
        return (evt.pos_y, evt.pos_x) == self.arrow_one_pos or \
                (evt.pos_y, evt.pos_x) == self.arrow_two_pos

    def _mouse_left_pressed(self, evt):
        if not self.within_arrow(evt):
            return
        self._arrow_released = False
        self._arrow_click_start(evt)

    def _mouse_left_released(self, evt):
        self._arrow_released = True
        self._arrow_click_end(evt)

    def _mouse_left_double_clicked(self, evt):
        if not self.within_arrow(evt):
            return
        self._arrow_click_start(evt)

    def _mouse_left_clicked(self, evt):
        if not self.within_arrow(evt):
            return
        self._arrow_click_start(evt)

    def _arrow_click_start(self, evt):
        if self._arrow_clicking:
            return
        self._arrow_clicking = True
        if (evt.pos_y, evt.pos_x) == self.arrow_one_pos:
            self.arrow_one_highlight = True
        else:
            self.arrow_two_highlight = True
        if self._arrow_released:
            timer = threading.Timer(0.1, self._arrow_click_end, [evt])
            timer.start()

    def _arrow_click_end(self, evt):
        if not self._arrow_clicking:
            return
        self._arrow_clicking = False
        if (evt.pos_y, evt.pos_x) == self.arrow_one_pos:
            self.arrow_one_highlight = False
            self.offset = self.offset - self.offset_step
        else:
            self.arrow_two_highlight = False
            self.offset = self.offset + self.offset_step


class ScrollHorizon(Scroll):
    """
    水平滚动条控件
    """
    def setup(self, full_width=1):
        super(ScrollHorizon, self).setup()
        self.full_width = full_width

    @property
    def arrow_one_pos(self):
        return (self.abs_y, self.abs_x)

    @property
    def arrow_two_pos(self):
        return (self.abs_y + self.height - 1, self.abs_x + self.width - 1)

    @property
    def max_offset(self):
        return self.full_width - self.width

    def paint(self):
        #self.cursor.reset()
        lwidth = self.width - 4
        self.cursor.move(0, 0)
        bar_width = max(1, lwidth * self.width // self.full_width)
        bar_offset = int(math.ceil(self.offset * self.width / self.full_width))
        bar_offset = min(lwidth - bar_width, bar_offset)
        bar_left = lwidth - bar_offset - bar_width
        if self.arrow_one_highlight:
            self.cursor.text(ARROW_LEFT, fcolor="black", bcolor="white")
        else:
            self.cursor.text(ARROW_LEFT)
        self.cursor.text(LINE_HORIZON * bar_offset + BAR_HORIZON * bar_width + \
          LINE_HORIZON * bar_left)
        if self.arrow_two_highlight:
            self.cursor.text(ARROW_RIGHT, fcolor="black", bcolor="white")
        else:
            self.cursor.text(ARROW_RIGHT)


class ScrollVertical(Scroll):
    """
    垂直滚动条控件
    """
    def setup(self, full_height=1):
        super(ScrollVertical, self).setup()
        self.full_height = full_height

    @property
    def arrow_one_pos(self):
        return (self.abs_y, self.abs_x)

    @property
    def arrow_two_pos(self):
        return (self.abs_y + self.height - 1, self.abs_x + self.width - 1)

    @property
    def max_offset(self):
        return self.full_height - self.height

    def paint(self):
        #self.cursor.reset()
        lheight = self.height - 2
        self.cursor.move(0, 0)
        if self.arrow_one_highlight:
            self.cursor.text(ARROW_UP, fcolor="black", bcolor="white")
        else:
            self.cursor.text(ARROW_UP)
        bar_height = max(1, lheight * self.height // self.full_height)
        bar_offset = int(math.ceil(self.offset * self.height / self.full_height))
        bar_offset = min(lheight - bar_height, bar_offset)
        bar_left = lheight - bar_offset - bar_height
        for i in range(bar_offset):
            self.cursor.nextline()
            self.cursor.text(LINE_VERTICAL)
        for i in range(bar_height):
            self.cursor.nextline()
            self.cursor.text(BAR_VERTICAL)
        for i in range(bar_left):
            self.cursor.nextline()
            self.cursor.text(LINE_VERTICAL)
        self.cursor.nextline()
        if self.arrow_two_highlight:
            self.cursor.text(ARROW_DOWN, fcolor="black", bcolor="white")
        else:
            self.cursor.text(ARROW_DOWN)

    def _mouse_scroll_up(self, evt):
        if not self.parent.within(evt.pos_y, evt.pos_x):
            return
        self.offset = self.offset - 1

    def _mouse_scroll_down(self, evt):
        if not self.parent.within(evt.pos_y, evt.pos_x):
            return
        self.offset = self.offset + 1


class Scrolled(Canvas):
    """
    可滚动控件
    """

    class VerticalScrolled(UIEvent):

        def __init__(self, delta):
            super(Scrolled.VerticalScrolled, self).__init__()
            self.delta = delta

    class HorizonScrolled(UIEvent):

        def __init__(self, delta):
            super(Scrolled.HorizonScrolled, self).__init__()
            self.delta = delta

    height = 2
    width = 4

    full_height = 50
    full_width = 50

    def setup(self, border=None):

        super(Scrolled, self).setup(border=border)

        self.substance = None

        self.scroll_h = ScrollHorizon(visible=False)
        self.scroll_v = ScrollVertical(visible=False)

        self.add(self.scroll_h)
        self.add(self.scroll_v)

        self.scroll_v.scrolled = self._vertical_scrolled
        self.scroll_h.scrolled = self._horizon_scrolled

        self.handler(Scrolled.VerticalScrolled, "vertical_scrolled")
        self.handler(Scrolled.HorizonScrolled, "horizon_scrolled")

    @property
    def iheight(self):
        if self.scroll_h.visible:
            return self.height - self.border_y * 2 - 1
        else:
            return self.height - self.border_y * 2
        
    @property
    def iwidth(self):
        if self.scroll_v.visible:
            return self.width - self.border_x * 2 - 2
        else:
            return self.width - self.border_x * 2

    def fill(self, substance):
        self.substance = substance
        self.add(substance)
        self.adjust()

    def size_changed(self):
        super(Scrolled, self).size_changed()
        self.adjust()

    def childsight(self, child):
        if child == self.scroll_h or child == self.scroll_v:
            child.resight(self.sight_y, self.sight_x, self.sight_height, self.sight_width)
        else:
            sight_height = self.iheight
            sight_width = self.iwidth
            sight = UI.recinter((self.sight_y, self.sight_x, self.sight_height, self.sight_width),
                                (self.abs_y + self.border_y, self.abs_x + self.border_x, sight_height, sight_width))
            child.resight(*sight)

    def _adjust(self):
        self.scroll_h.visible = False
        self.scroll_v.visible = False

        self.full_width = self.substance.width
        self.full_height = self.substance.height
        
        if self.full_width > self.width and self.full_height <= self.height:
            self.scroll_h.locate(pos_y=self.height - 1)
            self.scroll_h.resize(width=self.width)
            self.scroll_h.full_width = self.full_width
            self.scroll_h.visible = True
        elif self.full_width > self.width - 2 and self.full_height > self.height:
            self.scroll_h.locate(pos_y=self.height - 1)
            self.scroll_h.resize(width=self.width - 2)
            self.scroll_h.full_width = self.full_width
            self.scroll_h.visible = True
        if self.full_width <= self.width and self.full_height > self.height:
            self.scroll_v.locate(pos_x=self.width - 2)
            self.scroll_v.resize(height=self.height)
            self.scroll_v.full_height = self.full_height
            self.scroll_v.visible = True
        elif self.full_width > self.width and self.full_height > self.height - 1:
            self.scroll_v.locate(pos_x=self.width - 2)
            self.scroll_v.resize(height=self.height - 1)
            self.scroll_v.full_height = self.full_height
            self.scroll_v.visible = True

    def adjust(self):
        self.scroll_h.visible = False
        self.scroll_v.visible = False

        self.full_width = self.substance.width
        self.full_height = self.substance.height

        if self.full_width <= self.iwidth and self.full_height <= self.iheight:
            self.scroll_h.full_width = self.scroll_h.width
            self.scroll_v.full_height = self.scroll_v.height
        elif self.full_width > self.iwidth - 2 and self.full_height > self.iheight - 1:
            self.scroll_h.locate(pos_y=self.iheight - 1)
            self.scroll_h.resize(width=self.iwidth - 1)
            self.scroll_h.full_width = self.full_width
            self.scroll_v.locate(pos_x=self.iwidth - 1)
            self.scroll_v.resize(height=self.iheight - 1)
            self.scroll_v.full_height = self.full_height
            self.scroll_h.visible = True
            self.scroll_v.visible = True
        elif self.full_width > self.iwidth and self.full_height <= self.iheight - 1:
            self.scroll_h.locate(pos_y=self.iheight - 1)
            self.scroll_h.resize(width=self.iwidth)
            self.scroll_h.full_width = self.full_width
            self.scroll_h.visible = True
        elif self.full_width <= self.iwidth and self.full_height > self.iheight:
            self.scroll_v.locate(pos_x=self.iwidth - 1)
            self.scroll_v.resize(height=self.iheight)
            self.scroll_v.full_height = self.full_height
            self.scroll_v.visible = True

    def _vertical_scrolled(self, evt):
        if self.substance is None:
            return
        offset = -1 * evt.delta
        self.substance.move(offset_y=offset)
        self.event(Scrolled.VerticalScrolled(evt.delta))

    def _horizon_scrolled(self, evt):
        if self.substance is None:
            return
        offset = -1 * evt.delta
        self.substance.move(offset_x=offset)
        self.event(Scrolled.HorizonScrolled(evt.delta))
