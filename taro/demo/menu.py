import time

from taro.utils.log import LOG
from taro.core import Taro
from taro.controls.menu import Menu
from taro.controls.button import Button
from taro.controls.layout import LinearLayout

submenu = {}
pmenu = {}

class MyApp(Taro.App):

    def run(self):
        menu_c = Menu(width=16)
        menu_c.layout = LinearLayout(filled=True)
        menu_c.additem("SubItem1")
        menu_c.additem("SubItem2")
        menu_c.additem("Cancel")
        menu_c.off()

        menu_b = Menu(width=16)
        menu_b.layout = LinearLayout(filled=True)
        menu_b.additem("SubItem1", submenu=menu_c)
        menu_b.additem("SubItem2", submenu=menu_c)
        menu_b.additem("Cancel")
        menu_b.off()

        menu_a = Menu(width=16)
        menu_a.layout = LinearLayout(filled=True)
        menu_a.additem("Item1", submenu=menu_b)
        menu_a.additem("Item2", submenu=menu_b)
        menu_a.additem("Cancel")

        def popup(ctrl, evt):
            ctrl.menu.expand(ctrl)

        def cancel(ctrl, evt):
            ctrl.menu.shrink()

        def exit(ctrl, evt):
            Taro.shutdown()

        menu_a.items[0].clicked = popup
        menu_a.items[1].clicked = popup
        menu_a.items[2].clicked = exit

        menu_b.items[0].clicked = popup
        menu_b.items[1].clicked = popup
        menu_b.items[2].clicked = cancel

        menu_c.items[2].clicked = cancel


if __name__ == "__main__":
    Taro.runapp(MyApp)
