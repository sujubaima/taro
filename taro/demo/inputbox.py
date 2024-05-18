import time

from taro.core import Taro
from taro.core import UI
from taro.controls.canvas import Canvas
from taro.controls.inputbox import InputBox


class MyApp(Taro.App):

    def run(self):
        canvas = Canvas(height=6, width=16, border=True)
        input = InputBox(height=canvas.iheight, width=canvas.iwidth)
        canvas.add(input)
        input.active = True


if __name__ == "__main__":
    Taro.runapp(MyApp)
