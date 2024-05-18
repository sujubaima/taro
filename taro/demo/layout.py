from taro.core import Taro
from taro.utils.log import LOG
from taro.controls.layout import FlowLayout
from taro.controls.layout import LinearLayout
from taro.controls.layout import GridLayout
from taro.controls.canvas import Canvas
from taro.controls.button import Button


class LinearLayoutApp(Taro.App):

    def run(self):
        canvas_a = Canvas(height=4, width=40, border=True)
        canvas_b = Canvas(height=1, width=40)

        button_a = Button(text="OK")
        button_b = Button(text="Fuck")
        button_c = Button(text="Hi")

        canvas_a.layout = LinearLayout(lines=2)
        canvas_a.add(canvas_b, line=0)
        canvas_a.add(button_b, line=1)

        canvas_b.layout = FlowLayout()
        canvas_b.add(button_a)
        canvas_b.add(button_c)


class GridLayoutApp(Taro.App):

    def run(self):
        canvas_a = Canvas(height=4, width=40, border=True)

        button_a = Button(text="OK")
        button_b = Button(text="Fuck")
        button_c = Button(text="Hi")
        button_d = Button(text="Hello")

        canvas_a.layout = GridLayout(lines=2, columns=2)
        canvas_a.add(button_a, line=0, column=0)
        canvas_a.add(button_c, line=0, column=1)
        canvas_a.add(button_b, line=1, column=0)
        canvas_a.add(button_d, line=1, column=1)


if __name__ == "__main__":
    Taro.runapp(LinearLayoutApp)
    #Taro.runapp(GridLayoutApp)
