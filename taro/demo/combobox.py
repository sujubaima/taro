import logging

from taro.core import Taro
from taro.controls.label import Label
from taro.controls.combobox import ComboBox
from taro.controls.window import Window
from taro.controls.layout import FlowLayout


LOG = logging.getLogger()


class MyApp(Taro.App):

    def run(self):
        combobox = ComboBox(width=16)
        combobox.additem("Test1")
        combobox.additem("Test2")
        #combobox.additem("Test3")
        #combobox.additem("Test4")
        #combobox.additem("Test5")
        #combobox.additem("Test6")
        #combobox.additem("Test7")
        #combobox.additem("Test8")
        #combobox.additem("Test9")

        window = Window(width=36, height=5)
        window.layout = FlowLayout()
        window.add(Label(text="测试下拉框："))
        window.add(combobox)

        window.closed = lambda ctrl, evt: Taro.shutdown()


if __name__ == "__main__":
    Taro.runapp(MyApp)
