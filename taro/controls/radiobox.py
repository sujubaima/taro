import logging

from taro.core.event import UIEvent
from taro.controls.canvas import Canvas
from taro.controls.label import Label
from taro.controls.layout import FlowLayout


LOG = logging.getLogger()

UNSELECTED_ICON = "○ "
SELECTED_ICON = "◎ "


class RadioBoxItem(Label):

    _selected = False

    def setup(self, text=None):
        if text is None:
            text = ""
        self.radiobox = None
        self._raw_text = text
        super(RadioBoxItem, self).setup(text=UNSELECTED_ICON + self._raw_text)

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
        else:
            self.text = UNSELECTED_ICON + self._raw_text


class RadioBox(Canvas):

    class SelectionChanged(UIEvent):
        pass

    _selected = None

    def setup(self, title=None, border=None, fixed=False):
        self.items = []
        self._rawtext = {}
        super(RadioBox, self).setup(title=title, border=border, fixed=fixed)
        self.handler(RadioBox.SelectionChanged, "selection_changed")

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
            oldval.selected = False
        if val is not None:
            val.selected = True
        self.event(RadioBox.SelectionChanged())

    def additem(self, text, binddata=None):
        item = RadioBoxItem(text=text)
        item.binddata = binddata
        self._rawtext[item] = text
        self.items.append(item)
        super(RadioBox, self).add(item)
        return item
        
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
            if item != self.selected:
                self.selected = item
            break
