# -- coding: utf-8 --
import os
import re
import sys
import traceback
import platform
import time
import struct
import threading
import logging

import curses
import curses.ascii

from taro import options
from taro.utils.strutils import Colored
from taro.utils.strutils import strwidth
from taro.utils.strutils import unicoded


LOG = logging.getLogger()


AMAP = {
    "bold": curses.A_BOLD,
    "dark": curses.A_DIM,
    "underline": curses.A_UNDERLINE
}

CMAP = {
    "black": curses.COLOR_BLACK,
    "white": curses.COLOR_WHITE,
    "grey": curses.COLOR_BLACK,
    "red": curses.COLOR_RED,
    "yellow": curses.COLOR_YELLOW,
    "blue": curses.COLOR_BLUE,
    "cyan": curses.COLOR_CYAN,
    "green": curses.COLOR_GREEN,
    "magenta": curses.COLOR_MAGENTA
}

CPAIRS = {}


class UICursor(object):

    def __init__(self, cswin):
        self.cswin_ = cswin
        self.start_x = 0
        self.start_y = 0
        self.move(0, 0)

    def clone(self):
        ret = UICursor(self.cswin_)
        return ret

    def erase(self):
        self.cswin_.erase()

    def reset(self):
        self.cswin_.erase()
        self.move(0, 0)

    def resetline(self, y=None):
        if y is None:
            y = self.pos_y
        self.move(y, x=0)
        self.cswin_.clrtoeol()

    def move(self, y=None, x=None):
        if y is None:
            y = self.pos_y
        if x is None:
            x = self.pos_x
        try:
            self.cswin_.move(y + self.start_y, x + self.start_x)
            self.pos_x = x
            self.pos_y = y
        except curses.error:
            pass
    
    def up(self, step=1):
        return self.move(self.pos_y - step, self.pos_x)

    def down(self, step=1):
        return self.move(self.pos_y + step, self.pos_x)

    def left(self, step=1):
        return self.move(self.pos_y, self.pos_x - step)

    def right(self, step=1):
        return self.move(self.pos_y, self.pos_x + step)

    def nextline(self):
        return self.move(self.pos_y + 1, 0)

    def text(self, content="", fcolor="white", bcolor="black", attrs=[], y=None, x=None):
        if y is not None or x is not None:
            self.move(y, x)
        flag = 0
        if (fcolor, bcolor) not in CPAIRS:
            curses.init_pair(len(CPAIRS) + 1, CMAP[fcolor], CMAP[bcolor])
            CPAIRS[(fcolor, bcolor)] = len(CPAIRS) + 1
        cpr = CPAIRS[(fcolor, bcolor)]
        flag = 0
        for at in attrs:
            flag |= AMAP[at]
        try:
            self.cswin_.addstr(content, curses.color_pair(cpr) | flag)
        except curses.error as e:
            pass
        y, x = self.cswin_.getyx()
        max_y, max_x = self.cswin_.getmaxyx()
        if x == 0 and self.pos_y + self.start_y < y:
            self.pos_x = max_x - 1 - self.start_x
        else:
            self.pos_y = y - self.start_y
            self.pos_x = x - self.start_x

    def insert(self, content="", fcolor="white", bcolor="black", attrs=[], y=None, x=None):
        if y is not None or x is not None:
            self.move(y, x)
        flag = 0
        if (fcolor, bcolor) not in CPAIRS:
            curses.init_pair(len(CPAIRS) + 1, CMAP[fcolor], CMAP[bcolor])
            CPAIRS[(fcolor, bcolor)] = len(CPAIRS) + 1
        cpr = CPAIRS[(fcolor, bcolor)]
        flag = 0
        for at in attrs:
            flag |= AMAP[at]
        try:
            self.cswin_.insstr(content, curses.color_pair(cpr) | flag)
        except curses.error as e:
            pass
        y, x = self.cswin_.getyx()
        max_y, max_x = self.cswin_.getmaxyx()
        if x == 0 and self.pos_y + self.start_y < y:
            self.pos_x = max_x - 1 - self.start_x
        else:
            self.pos_y = y - self.start_y
            self.pos_x = x - self.start_x

    def textline(self, content="", fcolor="white", bcolor="black", attrs=[], y=None, x=None):
        self.text(content, fcolor=fcolor, bcolor=bcolor, attrs=attrs, y=x, x=x)
        try:
            self.move(self.pos_y + 1, 0)
        except Exception as e:
            pass

    def colortext(self, colored, y=None, x=None):
        if y is not None or x is not None:
            self.move(y, x)
        for s in colored.strlist:
            if not isinstance(s, list):
                self.text(s)
            else:
                self.text(s[0], fcolor=s[1], bcolor=s[2], attrs=s[3])

    def colorline(self, colored, y=None, x=None):
        self.colortext(colored, y=y, x=x)
        try:
            self.move(self.pos_y + 1, 0)
        except Exception as e:
            pass

    def char(self, y=None, x=None):
        if y is None:
            y = self.pos_y
        if x is None:
            x = self.pos_x
        return self.cswin_.inch(y + self.start_y, x + self.start_x)

    def rmchar(self, y=None, x=None):
        if y is None:
            y = self.pos_y
        if x is None:
            x = self.pos_x
        self.cswin_.delch(y + self.start_y, x + self.start_x)

    def show(self):
        curses.curs_set(1)

    def hide(self):
        curses.curs_set(0)
