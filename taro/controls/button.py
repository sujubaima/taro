import logging
import threading

from taro.core import UI
from taro.core import UIEvent
from taro.utils import strutils


LOG = logging.getLogger()

Colored = strutils.Colored


class Button(UI):

    height = 1

    _text = ""
    _raw_text = ""
    _highlight = False

    class ButtonClickedEvent(UIEvent):
        pass

    def setup(self, text):
        super(Button, self).setup()
        self.highlight = False
        self.text = text
        #self.clicked = lambda self, evt: None
        self.handler(Button.ButtonClickedEvent, "clicked")
        self._clicking = False

    def resize(self, height=None, width=None):
        """
        Overwrite the resize function of button.
        Button only support one-line mode.
        """
        super(Button, self).resize(width=width)
        self._text = strutils.align_center(self._raw_text, self.width - 2)

    @property
    def text(self):
        return self._raw_text

    @text.setter
    def text(self, text):
        if self._raw_text == text:
            return
        self._raw_text = text
        strwidth = strutils.strwidth(self._raw_text)
        if self.width < strwidth + 4:
            self.resize(width=strwidth + 4)
        else:
            self._text = strutils.align_center(self._raw_text, self.width - 2)#self._raw_text
        self.flag.modified()

    def paint(self):
        self.cursor.reset()
        if self.highlight:
            self.cursor.colortext("[" + Colored(self._text, fcolor="black", bcolor="white") + "]")
        elif not self.active:
            self.cursor.text("[" + self._text + "]", fcolor="grey", attrs=["bold"])
        else:
            self.cursor.text("[" + self._text + "]")

    def _mouse_left_pressed(self, evt):
        if not self.within(evt.pos_y, evt.pos_x):
            return
        self._click_start(evt, True)

    def _mouse_left_released(self, evt):
        if not self.within(evt.pos_y, evt.pos_x):
            self._clicking = False
            self.highlight = False
            return
        self._click_end(evt)

    def _mouse_left_double_clicked(self, evt):
        if not self.within(evt.pos_y, evt.pos_x):
            return
        self._click_start(evt)

    def _mouse_left_clicked(self, evt):
        if not self.within(evt.pos_y, evt.pos_x):
            return
        self._click_start(evt)

    def _click_start(self, evt, pressed=False):
        if self._clicking:
            return
        self._clicking = True
        self.highlight = True
        if not pressed:
            timer = threading.Timer(0.1, self._click_end, [evt])
            timer.start()

    def _click_end(self, evt):
        if not self._clicking:
            return
        self._clicking = False
        self.highlight = False
        #self.clicked(self, Button.ButtonClickedEvent())
        self.event(Button.ButtonClickedEvent())
