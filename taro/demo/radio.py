import time

from taro.core import Taro
from taro.utils.log import LOG
from taro.controls.canvas import Canvas
from taro.controls.label import Label
from taro.controls.radio import Radio
from taro.controls.layout import LinearLayout


class MyApp(Taro.App):

    def run(self):
        radio = Radio(width=20, height=7, title="测试单选框", border=Canvas.BD_STANDARD, fixed=True)
        radio.layout = LinearLayout(filled=True)
        radio.additem(Label(text="Test1"))
        radio.additem(Label(text="Test2"))
        radio.additem(Label(text="Test3"))
        radio.additem(Label(text="Test4"))
        radio.additem(Label(text="Test5"))


if __name__ == "__main__":
    Taro.runapp(MyApp)
