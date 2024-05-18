import time
import logging

from taro.core import Taro
from taro.controls.tab import TabGroup
from taro.controls.canvas import Canvas
from taro.controls.label import Label


LOG = logging.getLogger()


class MyApp(Taro.App):

    def run(self):
        tabgroup = TabGroup(height=12, width=40, mode=0)
        
        canvas_tab_a = Canvas(height=1, width=10)
        canvas_tab_b = Canvas(height=1, width=10)
        canvas_tab_c = Canvas(height=1, width=10)

        canvas_tab_a.add(Label(text="wordA"))
        canvas_tab_b.add(Label(text="wordB"))
        canvas_tab_c.add(Label(text="wordC"))

        tabgroup.addcanvas("TabA", canvas_tab_a, closable=True)
        tabgroup.addcanvas("TabB", canvas_tab_b, active=False, closable=True)
        tabgroup.addcanvas("TabCD", canvas_tab_c)



if __name__ == "__main__":
    Taro.runapp(MyApp)
