import threading
import logging

from taro.core import UI
from taro.utils import strutils
from taro.controls.label import Label
from taro.controls.canvas import Canvas
from taro.controls.scrolled import Scrolled
from taro.controls.layout import LinearLayout


LOG = logging.getLogger()

ARROW_DOWN = "▼"


class DropDown(Scrolled):

    _clicking = False

    def setup(self, combo):
        super(DropDown, self).setup(border=Canvas.BD_STANDARD)
        self._canvas = Canvas(width=self.iwidth, fixed=False)
        self._canvas.layout = LinearLayout()
        self.fill(self._canvas)
        self.combo = combo

    def paint(self):
        super(DropDown, self).paint()
        self.cursor.move(-1, -2)
        txt = ""
        if self.combo.selected is not None:
            txt = self.combo.selected.text
        self.cursor.text(txt + " " * (self.width - strutils.strwidth(txt)), attrs=["underline"])

    def _additem(self, item):
        #if item.width > self._canvas.width:
        #    self._canvas.resize(width=item.width)
        self._canvas.add(item)
        self.adjust()

    def removeitem(self, item):
        self.scroll_v.offset = 0
        self._canvas.remove(item)
        self.adjust()

    def _mouse_left_pressed(self, evt):
        if self.within(evt.pos_y, evt.pos_x):
            self._click_start(evt, pressed=True)

    def _mouse_left_clicked(self, evt):
        if not self.within(evt.pos_y, evt.pos_x):
            self.combo.shrink()
        else:
            self._click_start(evt)

    def _mouse_left_released(self, evt):
        if not self.within(evt.pos_y, evt.pos_x):
            self.combo.shrink()
        else:
            self._click_end(evt)

    def _click_start(self, evt, pressed=False):
        if self._clicking:
            return
        self._clicking = True
        for item in self.combo.items:
            if item.within(evt.pos_y, evt.pos_x) and \
               evt.pos_x <= self.sight_x + self.sight_width:
                item.highlight = True
                break
        if not pressed:
            timer = threading.Timer(0.1, self._click_end, [evt])
            timer.start()

    def _click_end(self, evt):
        if not self._clicking:
            return
        for item in self.combo.items:
            if item.highlight:
            #if item.within(evt.pos_y, evt.pos_x) and \
            #   evt.pos_x <= self.sight_x + self.sight_width:
                item.highlight = False
                self.combo.selected = item
                break
        self.combo.shrink()
        self._clicking = False


class ComboBox(UI):

    _selected = None

    _text = ""

    _all = []

    selected_item_changed = lambda ctrl: None

    def setup(self, showsize=5):
        ComboBox._all.append(self)
        self.expanded = False
        self.items = []
        super(ComboBox, self).setup()
        self.showsize = showsize
        #self._dropdown = Canvas(height=showsize + 2, width=self.width - 1, border=Canvas.BD_STANDARD)
        self._dropdown = DropDown(height=3, width=self.width - 2, combo=self)
        #self._scrolled = Scrolled(height=self._dropdown.iheight, width=self._dropdown.iwidth)
        #self._canvas = Canvas(width=self._scrolled.width - 2, fixed=False)
        #self._canvas.layout = LinearLayout()
        #self._scrolled.fill(self._canvas)
        #self._dropdown.add(self._scrolled)
        self._dropdown.off()

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, val):
        if self._selected == val:
            return
        oldval = self._selected
        self._selected = val
        self.selected_item_changed()

    def paint(self):
        self.cursor.move(0, 0)
        txt = ""
        if self.selected is not None:
            txt = self.selected.text
        self.cursor.text(txt + " " * (self.width - 2 - strutils.strwidth(txt)), attrs=["underline"])
        self.cursor.text(" ")
        self.cursor.text(ARROW_DOWN)

    def additem(self, item, binddata=None):
        item = Label(text=item)
        item.resize(width=max(self._dropdown._canvas.width, item.width))
        item.binddata = binddata
        self.items.append(item)
        if len(self.items) <= self.showsize:
            self._dropdown.resize(height=len(self.items) + 2)
        #if item.width > self._canvas.width:
        #    self._canvas.resize(width=item.width)
        #self._canvas.add(item)
        #self._scrolled.adjust()
        self._dropdown._additem(item)
        return item

    def removeitem(self, item):
        if self.selected == item:
            self.selected = None
        self.items.remove(item)
        if len(self.items) <= self.showsize and len(self.items) > 0:
            self._dropdown.resize(height=len(self.items) + 2)
        self._dropdown.removeitem(item)

    def clearitems(self):
        while len(self.items) > 0:
            self.removeitem(self.items[0])
        
    def _mouse_left_released(self, evt):
        if not self.within(evt.pos_y, evt.pos_x):
            self.shrink()
        else:
            self.expand()

    def _mouse_left_clicked(self, evt):
        if not self.within(evt.pos_y, evt.pos_x):
            self.shrink()
        else:
            self.expand()

    def expand(self):
        for combo in ComboBox._all:
            if not combo.expanded:
                continue
            combo.shrink()
            if combo == self:
                return
        if not self.expanded:
            #for ctrl in UI.All.values():
                #if ctrl == UI.Root:
                #    continue
                #if not ctrl.active:
                #    continue
                #if ctrl in self.items:
                #    continue
            for ctrl in UI.Root.children:
                if not ctrl.active:
                    continue
                UI._stack.append(ctrl)
                ctrl.active = False
            self._dropdown.locate(self.abs_y, self.abs_x)
            self._dropdown.upper()
            self._dropdown.on()
            self.expanded = True

    def shrink(self):
        if self.expanded:
            while len(UI._stack) > 0:
                ctrl = UI._stack.pop()
                ctrl.active = True
            self._dropdown.off()
            self.expanded = False
