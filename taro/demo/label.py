import time

from taro.core import Taro
from taro.utils import Colored
from taro.controls.label import Label


class MyApp(Taro.App):

    def run(self):
        #text = Label(text="Button")
        #text = Colored("abcdefghijklmnopqrstuvwxyz", fcolor="red") + Colored("ABCDEFGHIJKLMNOPQRSTUVWXYZ", fcolor="yellow")
        #text.rearrange(10)
        text = Colored(" " * 9, fcolor="white", attrs=["underline"])
        label = Label(text=text)


if __name__ == "__main__":
    Taro.runapp(MyApp)
