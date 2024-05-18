# -- coding: utf-8 --
import struct
import logging

import curses
import curses.ascii

from taro.core import UI
from taro.core.event import UIEvent
from taro.utils import strutils


LOG = logging.getLogger()


class InputBox(UI):

    class TextChanged(UIEvent):
        pass

    def setup(self, text=None):
        super(InputBox, self).setup()
        self._charbuf = []
        #self._init = False
        if text is not None:
            self._text = text
        else:
            self._text = ""
        self._init_text()

        self.handler(InputBox.TextChanged, "text_changed")

    @property
    def text(self):
        return str(self._text)

    @text.setter
    def text(self, val):
        if self._text == val:
            return
        self._text = val
        self._init_text()
        self.flag.modified()

    def _init_text(self):
        if self.active:
            fcolor = "white"
            attrs = ["underline"]
        else:
            fcolor = "grey" 
            attrs = ["bold", "underline"]
        self.cursor.move(0, 0)
        self.cursor.text(" " * self.width, attrs=attrs)
        self.cursor.move(0, 0)
        if len(self._text) != 0:
            self.cursor.text(self._text, fcolor=fcolor, attrs=attrs)

    #def paint(self):
        #if not self._init:
        #    self.cursor.move(0, 0)
        #    self.cursor.text(" " * self.width, attrs=["underline"])
        #    self.cursor.move(0, 0)
        #    self._init = True
        #if UI.Focused == self:
        #    curses.curs_set(1)
        #    self._record_cursor()
        #else:
        #    curses.curs_set(0)

    def _mouse_left_released(self, evt):
        if not self.within(evt.pos_y, evt.pos_x):
            if UI.Focused == self:
                UI.Focused = None
                self.flag.modified()
        else:
            UI.Focused = self
            self.flag.modified()

    def _mouse_left_clicked(self, evt):
        if not self.within(evt.pos_y, evt.pos_x):
            if UI.Focused == self:
                UI.Focused = None
                self.flag.modified()
        else:
            UI.Focused = self
            self.flag.modified()

    def utfize(self, arg):
        if arg < 32 or arg > 255:
            return arg
        self._charbuf.append(arg)
        b = struct.pack("B" * len(self._charbuf), *self._charbuf)
        ret = ""
        try:
            ret = b.decode("utf-8")#.encode("utf-8")
            self._charbuf = []
        except Exception as e:
            pass
        return ret

    def _key_input(self, evt):
        if UI.Focused != self:
            return
        key = evt.key
        y = self.cursor.pos_y
        x = self.cursor.pos_x
        if key == curses.ascii.TAB:
            return
        elif key in (curses.ascii.STX, curses.KEY_LEFT, curses.ascii.BS,curses.KEY_BACKSPACE):
            uchar_1 = chr((self.cursor.char(y, x - 2) if x >= 2 else 1) & ~curses.A_UNDERLINE)
            uchar_2 = chr((self.cursor.char(y, x - 1) if x >= 2 else 1) & ~curses.A_UNDERLINE)
            if u'\u4e00' <= uchar_1 and uchar_1 <= u'\u9fff' and u'\u4e00' <= uchar_2 and uchar_2 <= u'\u9fff':
                mv_step = 2
            else:
                mv_step = 1
            if x > mv_step - 1:
                self.cursor.move(y, x - mv_step)
            elif y == 0:
                pass
            else:
                self.cursor.move(y - 1, x)
            if key in (curses.ascii.BS, curses.KEY_BACKSPACE):
                self.cursor.rmchar()
                if mv_step == 2:
                    self.cursor.rmchar()
                self.cursor.insert(" " * mv_step, attrs=["underline"])
                self.text = self.text[:-1]
                self.event(InputBox.TextChanged())
        elif key in (curses.ascii.ACK, curses.KEY_RIGHT):
            uchar = chr(self.cursor.char(y, x))
            if u'\u4e00' <=  uchar and uchar <= u'\u9fff':
                mv_step = 2
            else:
                mv_step = 1
            if x < self.width - mv_step:
                self.cursor.move(y, x + mv_step)
            elif y == self.height - 1:
                pass
            else:
                self.cursor.move(y + 1, 0)
        elif key == curses.KEY_DOWN:
            self.cursor.down()
        elif key == curses.KEY_UP:
            self.cursor.up()
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            self.cursor.nextline()
        else:
            txt = self.utfize(key)
            strwidth = 0
            try:
                strwidth = strutils.strwidth(txt)
            except Exception as e:
                pass
            if strwidth > 0 and x < self.width - strwidth:
                self.cursor.text(txt, attrs=["underline"])
                self.text += txt
                self.event(InputBox.TextChanged())
                #self.cursor.text(txt)
        self.flag.moved()
