from taro.core import Taro
from taro.core import UI
from taro.controls.window import Window
from taro.controls.image import ImageCanvas
from taro.controls.layout import FillLayout


class MyApp(Taro.App):

    def run(self):
        height = min(UI.ScreenWidth // 2, UI.ScreenHeight)
        width = 2 * height

        window_a = Window(title="大恐龙", height=height, width=width)
        window_a.layout = FillLayout()
        window_a.add(ImageCanvas(imgsrc="images/xine.png"))

        #window_b = Window(height=35, width=70)
        #window_b.layout = FillLayout()
        #window_b.add(ImageCanvas(imgsrc="images/xine.png"))

        #window_b.locate(8, 50)


if __name__ == "__main__":
    Taro.runapp(MyApp)
