# -- coding: utf-8 --
import logging

from taro.core import UI

import curses
import curses.ascii

LOG = logging.getLogger()


class Canvas(UI):
    """
    画布为所有可以由边框围起来空白区域的基类
    通常用于将一堆组件整合成一个，可配合UIView使用
    """
    BD_NULL = 0
    BD_STANDARD = 1
    BD_CORNER = 2

    _layout = None

    _title = None

    def setup(self, title=None, border=None, shadow=False, fixed=True):
        super(Canvas, self).setup()
        self.fixed = fixed
        self.view = None
        #self.substance = None
        if border is None or border == Canvas.BD_NULL:
            self.border = Canvas.BD_NULL
            self.border_y = 0
            self.border_x = 0
        else:
            self.border = border
            self.border_y = 1
            self.border_x = 2
            self.cursor.start_y = 1
            self.cursor.start_x = 2
        if title is not None:
            self.title = title
        self.shadow = shadow
        if self.shadow:
            self.shade_left = UI(height=self.height, width=1, visible=False)
            self.shade_right = UI(height=self.height, width=1, visible=False)
            self._shades()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        if self._title == title:
            return
        self._title = title
        self.flag.modified()

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, val):
        if self._layout is not None:
            self.remove(self._layout)
            self._layout = None
        self.add(val)
        self._layout = val
        if self._layout is not None:
            self._layout.locate(0, 0)
            self._layout.resize(self.iheight, self.iwidth)

    @property
    def iheight(self):
        return self.height - self.border_y * 2

    @property
    def iwidth(self):
        return self.width - self.border_x * 2

    def to_abs(self, pos_y, pos_x):
        return (self.abs_y + self.border_y + pos_y, self.abs_x + self.border_x + pos_x)

    def to_pos(self, abs_y, abs_x):
        return (abs_y - self.border_y - self.abs_y, abs_x - self.border_x - self.abs_x)

    def on(self):
        super(Canvas, self).on()
        if self.shadow:
            self.shade_left.on()
            self.shade_right.on()

    def off(self):
        super(Canvas, self).off()
        if self.shadow:
            self.shade_left.off()
            self.shade_right.off()

    def locate(self, pos_y=None, pos_x=None):
        super(Canvas, self).locate(pos_y=pos_y, pos_x=pos_x)
        if self.shadow:
            self._shades()

    def coordinate(self):
        if self.parent is not None:
            self.coord_x = self.parent.coord_x + self.parent.pos_x
            self.coord_y = self.parent.coord_y + self.parent.pos_y
        self.abs_x = self.coord_x + self.pos_x
        self.abs_y = self.coord_y + self.pos_y
        self.coord_y += self.border_y
        self.coord_x += self.border_x
        for child in self.children:
            child.coordinate()

    def add(self, child, *args, **kwargs):
        if self.layout is None:
            super(Canvas, self).add(child, *args, **kwargs)
            pos_y = kwargs.get("pos_y")
            pos_x = kwargs.get("pos_x")
            child.locate(pos_y=pos_y, pos_x=pos_x)
        else:
            self.layout.add(child, *args, **kwargs)
            if not self.fixed:
                self.resize(max(1, self.layout.height + 2 * self.border_y),
                            max(1, self.layout.width + 2 * self.border_x))

    def remove(self, child, *args, **kwargs):
        if self.layout is None or child == self.layout:
            super(Canvas, self).remove(child, *args, **kwargs)
        else:
            self.layout.remove(child, *args, **kwargs)
            if not self.fixed:
                self.resize(max(1, self.layout.height + 2 * self.border_y),
                            max(1, self.layout.width + 2 * self.border_x))

    def childsight(self, child):
        sight = UI.recinter((self.sight_y, self.sight_x, self.sight_height, self.sight_width),
                            (self.abs_y + self.border_y, self.abs_x + self.border_x,
                             self.iheight, self.iwidth))
        child.resight(*sight)

    def size_changed(self):
        self.resight()
        if self.layout is not None:
            self.layout.resize(self.iheight, self.iwidth)
            self.layout.arrange()

    def paint(self):
        self._paint_border()
        self._paint_title()
        if self.shadow:
            self._shades()

    def _paint_border(self):
        #if self.border == 1:
        #    self.cursor.cswin_.border()
        #elif self.border == 2:
        #    self.cursor.cswin_.box(" ", " ")
        if self.active:
            fcolor, attrs = "white", []
        else:
            fcolor, attrs = "grey", ["bold"]
        if self.border > 0:
            self.cursor.text(
                "┌", 
                fcolor=fcolor, 
                attrs=attrs, 
                y=-1, 
                x=-2
            )
            self.cursor.text(
                "┐", 
                fcolor=fcolor, 
                attrs=attrs, 
                y=-1, 
                x=self.width - self.border_x - 1
            )
            self.cursor.text(
                "└", 
                fcolor=fcolor, 
                attrs=attrs, 
                y=self.height - self.border_y - 1, 
                x=-2
            )
            self.cursor.text(
                "┘", 
                fcolor=fcolor, 
                attrs=attrs, 
                y=self.height - self.border_y - 1, 
                x=self.width - self.border_x - 1
            )
        if self.border == 1:
            self.cursor.text(
                "─" * (self.width - 2), 
                fcolor=fcolor, 
                attrs=attrs, 
                y=-1, 
                x=-1
            )
            self.cursor.text(
                "─" * (self.width - 2), 
                fcolor=fcolor, 
                attrs=attrs, 
                y=self.height - self.border_y - 1, 
                x=-1
            )
            for i in range(self.height - 2):
                self.cursor.text(
                    "│", 
                    fcolor=fcolor, 
                    attrs=attrs, 
                    y=i, 
                    x=-2
                )
                self.cursor.text(
                    "│", 
                    fcolor=fcolor, 
                    attrs=attrs, 
                    y=i, 
                    x=self.width - self.border_x - 1
                )

    def _paint_title(self):
        if self.title is not None:
            self.cursor.move(-1, -1)
            self.cursor.text(" " + self.title + " ")

    def _shades(self):
        self.shade_left.zindex = self.zindex
        self.shade_right.zindex = self.zindex
        self.shade_left.locate(pos_y=self.abs_y, pos_x=self.abs_x - 1)
        self.shade_right.locate(pos_y=self.abs_y, pos_x=self.abs_x + self.width)
        if self.shade_left.abs_x < 0:
            self.shade_left.visible = False
        elif self.visible:
            self.shade_left.visible = True
        if self.shade_right.abs_x >= UI.ScreenWidth:
            self.shade_right.visible = False
        elif self.visible:
            self.shade_right.visible = True

    def upper(self):
        self.zindex = self.parent.uppermost + 1
        if self.shadow:
            self.shade_left.zindex = self.zindex
            self.shade_right.zindex = self.zindex

    def lower(self):
        self.zindex = 0
        if self.shadow:
            self.shade_left.zindex = 0
            self.shade_right.zindex = 0

    def destroy(self):
        if self.shadow:
            self.shade_left.destroy()
            self.shade_right.destroy()
        super(Canvas, self).destroy()
