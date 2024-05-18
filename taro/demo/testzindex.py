import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../.."))

from taro.core import Taro
from taro.controls.window import Window
from taro.controls.button import Button


clicked_times = {}


class MyApp(Taro.App):

    def run(self):
        window_a = Window(height=20, width=40, title="NewWindow")
        button_a = Button(text="OK")
        window_a.add(button_a, pos_y=window_a.iheight - 1)

        window_b = Window(height=20, width=40, title="NewWindow")
        button_b = Button(text="OK")
        window_b.add(button_b, pos_y=window_b.iheight - 1)

        window_b.locate(pos_y=18, pos_x=60)

        def button_clicked(ctrl, evt):
            global clicked_times
            clicked_times[ctrl.parent.id] = clicked_times.get(ctrl.parent.id, 0) + 1
            ctrl.parent.title = "Clicked %s" % clicked_times[ctrl.parent.id]

        button_a.clicked = button_clicked
        button_b.clicked = button_clicked


if __name__ == "__main__":
    Taro.runapp(MyApp)
