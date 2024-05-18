from taro.core import Taro
from taro.controls.window import Window
from taro.controls.button import Button


clicked_times = 0


class MyApp(Taro.App):

    def run(self):
        window = Window(height=20, width=40, title="NewWindow")
        button = Button(text="OK")
        window.add(button, pos_y=window.iheight - 1)

        def button_clicked(ctl, evt):
            global clicked_times
            clicked_times += 1
            window.title = "Clicked %s" % clicked_times

        def window_closed(ctl, evt):
            Taro.shutdown()

        button.clicked = button_clicked
        window.closed = window_closed


if __name__ == "__main__":
    Taro.runapp(MyApp)
