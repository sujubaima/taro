import time

from taro.core import Taro
from taro.controls.canvas import Canvas
from taro.controls.inputbox import InputBox


class MyApp(Taro.App):

    def run(self):
        input = InputBox(width=9)
        input.active = True


if __name__ == "__main__":
    Taro.runapp(MyApp)
