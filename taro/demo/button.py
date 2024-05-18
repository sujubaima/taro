import time

from taro.core import Taro
from taro.controls.button import Button


class MyApp(Taro.App):

    def run(self):
        #a = TestUI(height=UI.ScreenHeight, width=UI.ScreenWidth)
        #time.sleep(10)
        button = Button(text="Button")


if __name__ == "__main__":
    Taro.runapp(MyApp)
