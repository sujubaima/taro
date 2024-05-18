import logging

from taro.core import UI
from taro.core.event import UIEvent
from taro.core.event import MouseLeftDoubleClicked
from taro.utils import strutils
from taro.controls.label import Label
from taro.controls.canvas import Canvas
from taro.controls.scrolled import Scrolled
from taro.controls.layout import LinearLayout


LOG = logging.getLogger()

ARROW_DOWN = "▼"


class ListBox(Scrolled):

    class ItemChanged(UIEvent):
        pass

    class ItemDoubleClicked(UIEvent):
        pass

    _selected = None

    def setup(self):
        super(ListBox, self).setup(border=Canvas.BD_STANDARD)
        self._canvas = Canvas(width=self.iwidth, fixed=False)
        self._canvas.layout = LinearLayout()
        self.fill(self._canvas)
        self.items = []

        self.handler(ListBox.ItemChanged, "item_changed")
        self.handler(ListBox.ItemDoubleClicked, "item_double_clicked")

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
        self.event(ListBox.ItemChanged())

    def additem(self, item, binddata=None):
        item = Label(text=item)
        item.resize(width=max(self._canvas.width, item.width))
        self.addcontrol(item, binddata=binddata)
        self.flag.modified()

    def addcontrol(self, item, binddata=None):
        item.binddata = binddata
        self.items.append(item)
        if item.width > self._canvas.width:
            self._canvas.resize(width=item.width)
        self._canvas.add(item)
        self.adjust()
        return item

    def removeitem(self, item):
        if self.selected == item:
            self.selected = None
        self.items.remove(item)
        self._canvas.remove(item)
        self.adjust()
        self.flag.modified()

    def clearitems(self):
        while len(self.items) > 0:
            self.removeitem(self.items[0])

    def _mouse_left_released(self, evt):
        if not self.within(evt.pos_y, evt.pos_x):
            return
        self._left_clicked(evt)

    def _mouse_left_clicked(self, evt):
        if not self.within(evt.pos_y, evt.pos_x):
            return
        self._left_clicked(evt)

    def _mouse_left_double_clicked(self, evt):
        if not self.within(evt.pos_y, evt.pos_x):
            return
        self._left_clicked(evt)

    def _left_clicked(self, evt):
        changed = False
        for item in self.items:
            if not item.active:
                continue
            #if evt.pos_y >= item.abs_y and evt.pos_y < item.abs_y + item.height:
            if not item.within(evt.pos_y, evt.pos_x):
                continue
            if item != self.selected: 
                #changed = True
                self.selected = item
            break
        #if changed:
        #    self.item_changed(self, evt)
        if evt.__class__ == MouseLeftDoubleClicked:
            self.event(ListBox.ItemDoubleClicked())
