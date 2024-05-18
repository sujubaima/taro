import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../.."))

from taro.core import Taro
from taro.controls.window import Window
from taro.controls.scrolled import Scrolled
from taro.controls.canvas import Canvas
from taro.controls.button import Button


clicked_times = 0


class MyApp(Taro.App):

    def run(self):
        window = Window(height=20, width=40, title="NewWindow")
        scroll = Scrolled(height=window.iheight - 1, width=window.iwidth)
        canvas = Canvas(height=60, width=60)
        for i in range(60):
            canvas.cursor.textline("This is line %s" % i)
        window.add(scroll)
        scroll.fill(canvas)

        button = Button(text="OK")
        window.add(button, pos_y=window.iheight - 1)

        def button_clicked(evt):
            global clicked_times
            clicked_times += 1
            window.title = "Clicked %s" % clicked_times

        def window_closed(evt):
            Taro.shutdown()

        button.clicked = button_clicked
        window.closed = window_closed
        window.locate(2, 2)


if __name__ == "__main__":
    Taro.runapp(MyApp)
