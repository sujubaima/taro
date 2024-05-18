# -- coding: utf-8 --
import logging

from taro.utils import strutils
from taro.core import UI


LOG = logging.getLogger()


class Label(UI):
    """
    基础文字控件
    """
    _text = ""

    def setup(self, text=None, fixed=False):
        super(Label, self).setup()
        self.fixed = fixed
        self._lines = []
        if text is not None:
            self.text = text
    
    @property
    def text(self):
        return str(self._text)

    @text.setter
    def text(self, val):
        if self._text == val:
            return
        #self.cursor.erase()
        #self.refresh()
        self._text = val
        self._lines = self._text.split("\n")
        self.adjust()

    @property
    def lines(self):
        return self._lines

    @lines.setter
    def lines(self, val):
        if self._lines == val:
            return
        self._lines = val
        self.adjust()

    def resize(self, height=None, width=None):
        super(Label, self).resize(height=height, width=width)
        for i in range(len(self._lines)):
            self._lines[i] = strutils.align_left(self._lines[i], self.width)

    def adjust(self):
        if not self.fixed:
            twidth = 0
            theight = len(self._lines)
            for line in self._lines:
                twidth = max(twidth, strutils.strwidth(line))
            #twidth = max(twidth, self.width)
            twidth = max(twidth, 1)
            self.resize(height=theight, width=twidth)
        else:
            self.resize(height=self.height, width=self.width)
        self.flag.modified()

    def paint(self):
        self.cursor.move(0, 0)
        for line in self._lines:
            if not self.active:
                self.cursor.textline(str(line), fcolor="grey", attrs=["bold"])
            elif self.highlight:
                self.cursor.textline(str(line), fcolor="black", bcolor="white")
            else:
                if isinstance(line, strutils.Colored):
                    self.cursor.colorline(line)
                else:
                    self.cursor.textline(line)
        if len(self._lines) >= self.height:
            return
        for i in range(self.height - len(self._lines)):
            self.cursor.textline(" " * self.width)
