# -- coding: utf-8 --
import logging

from taro.utils.strutils import strwidth
from taro.utils.strutils import Colored
from taro.core import UI


LOG = logging.getLogger()


class Text(UI):
    """
    基础文字控件
    """
    _content = None

    def setup(self, content=None):
        super(Text, self).setup()
        if content is None:
            content = []
        if not isinstance(content, list):
            self.content = [content]
        else:
            self.content = content
    
    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, val):
        if self._content == val:
            return
        self._content = val
        self.adjust()
        self.flag.modified()

    def adjust(self):
        max_width = 0
        for line in self.content:
            max_width = max(max_width, strwidth(line))
        max_height = len(self.content)
        width = max(self.width, max_width)
        height = max(self.height, max_height)
        self.resize(height, width)

    def paint(self):
        self.cursor.reset()
        for line in self.content:
            if isinstance(line, Colored):
                self.cursor.colorline(line)
            else:
                self.cursor.textline(line)
