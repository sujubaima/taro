import time

from proj.ui.app import UIApp
from proj.ui.terminal.core import UI
from proj.ui.terminal.core import UIControl
from proj.ui.terminal.button import Button


class TestUI(UIControl):

    def _mouse_left_released(self, evt):
        self._left_clicked(evt)

    def _mouse_left_clicked(self, evt):
        self._left_clicked(evt)

    def _mouse_right_released(self, evt):
        self._right_clicked(evt)

    def _mouse_right_clicked(self, evt):
        self._right_clicked(evt)

    def _mouse_scroll_up(self, evt):
        self.cursor.textline("Scroll Up")
        self.flag.modified()

    def _mouse_scroll_down(self, evt):
        self.cursor.textline("Scroll Down")
        self.flag.modified()

    def _left_clicked(self, evt):
        self.cursor.move(evt.pos_y, evt.pos_x)
        self.cursor.text("Left Clicked")
        self.flag.modified()

    def _right_clicked(self, evt):
        self.cursor.move(evt.pos_y, evt.pos_x)
        self.cursor.text("Right Clicked")
        self.flag.modified()


class MyApp(UIApp):

    def run(self):
        a = TestUI(height=UI.ScreenHeight, width=UI.ScreenWidth)
        time.sleep(10)


if __name__ == "__main__":
    UI.runapp(MyApp)
