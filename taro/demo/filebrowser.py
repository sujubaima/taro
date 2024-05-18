import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../.."))

from taro.core import Taro
from taro.controls.filebrowser import FileBrowser


class MyApp(Taro.App):

    def run(self):
        browser = FileBrowser(height=20, width=40, pwd=".", writable=False)


if __name__ == "__main__":
    Taro.runapp(MyApp)
