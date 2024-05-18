import time
import logging

from taro.core import Taro
from taro.controls.canvas import Canvas
from taro.controls.label import Label
from taro.controls.checkbox import CheckBox
from taro.controls.layout import LinearLayout

LOG = logging.getLogger()


class MyApp(Taro.App):

    def run(self):
        checkbox = CheckBox(width=20, height=7, title="测试多选框", border=Canvas.BD_STANDARD, fixed=True)
        checkbox.layout = LinearLayout(filled=True)
        checkbox.additem("Test1")
        checkbox.additem("Test2")
        checkbox.additem("Test3")
        checkbox.additem("Test4")
        checkbox.additem("Test5")


if __name__ == "__main__":
    Taro.runapp(MyApp)
