import logging

from taro.core import UI
from taro.core.event import UIEvent
from taro.controls.canvas import Canvas
from taro.controls.label import Label
from taro.controls.layout import LinearLayout


LOG = logging.getLogger()

UNSELECTED_ICON = "□ "
SELECTED_ICON = "▣ "


class CheckBoxItem(Label):

    _selected = False

    def setup(self, text=None):
        if text is None:
            text = ""
        self.checkbox = None
        self._raw_text = text
        super(CheckBoxItem, self).setup(text=UNSELECTED_ICON + self._raw_text)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, val):
        if self._selected == val:
            return
        self._selected = val
        if self._selected:
            self.text = SELECTED_ICON + self._raw_text
            self.checkbox.selected.append(self)
        else:
            self.text = UNSELECTED_ICON + self._raw_text
            self.checkbox.selected.remove(self)
        self.checkbox.event(CheckBox.SelectionChanged())


class CheckBox(Canvas):

    class SelectionChanged(UIEvent):
        pass

    def setup(self, title=None, border=None, fixed=False):
        self.items = []
        self.selected = []
        super(CheckBox, self).setup(title=title, border=border, fixed=fixed)
        self.layout = LinearLayout(filled=True)
        self.handler(CheckBox.SelectionChanged, "selection_changed")

    def additem(self, text, binddata=None):
        item = CheckBoxItem(text=text)
        item.checkbox = self
        if self.resizable:
            self.resize(width=max(self.width, item.width))
        item.binddata = binddata
        self.items.append(item)
        super(CheckBox, self).add(item)
        return item

    def removeitem(self, item):
        if item in self.selected:
            self.selected.remove(item)
        self.items.remove(item)
        self.remove(item)

    def clearitems(self):
        while len(self.items) > 0:
            self.removeitem(self.items[0])
        
    def _mouse_left_released(self, evt):
        self._left_clicked(evt)

    def _mouse_left_clicked(self, evt):
        self._left_clicked(evt)

    def _left_clicked(self, evt):
        changed = False
        for item in self.items:
            if not item.active:
                continue
            if not item.within(evt.pos_y, evt.pos_x):
                continue
            if item.selected:
                item.selected = False
            else:
                item.selected = True
            break
