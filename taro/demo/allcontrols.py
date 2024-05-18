import os
import sys
import logging

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../.."))

from taro.core import Taro
from taro.core import UI
from taro.controls import Canvas
from taro.controls import Label
from taro.controls import Window
from taro.controls import Button
from taro.controls import GridLayout
from taro.controls import LinearLayout
from taro.controls import CheckBox
from taro.controls import RadioBox
from taro.controls import ListBox
from taro.controls import ComboBox
from taro.controls import TabGroup

LOG = logging.getLogger()

combo_data = {"武器": ["真尼斯之杖", "圣剑", "屠龙者", "黑铁长枪", "格斗拳套", "龙牙匕首", "紫衫木长弓"], 
              "防具": ["幽邃法衣", "秘银锁甲"]}

words_a = "来自阿洛伊斯王国的骑士。\n" + \
          "他们负责维护光明之神的权威，对于异端之人无可容忍。\n" + \
          "他们坚信自己拥有被光明之神祝福过的\"圣剑\"，可以轻易将\n" + \
          "污秽之物一刀两断。"

words_b = "在阿洛伊斯王国，死灵术是禁术。\n" + \
          "不过依然有很多向往黑暗的法师在秘密修行。\n" + \
          "相传死灵术可以控制生物死去后的肉体和灵魂。\n" + \
          "但也有另一种说法，修行死灵术的人会把自己变成行尸走肉。"

words_c = "在讨伐魔王的过程中不幸堕落的冒险者，现在变成了魔王的爪\n" + \
          "牙。\n" + \
          "据说所有的恶堕之人都是男性。\n" + \
          "而那些被拉入黑暗的女人们，她们究竟身处何方呢？"

checkbox_data = ["元素魔法专精", "死灵魔法专精", "自然魔法专精", "单手武器专精", "长柄武器专精", "盾牌专精"]

radiobox_data = ["人类", "精灵", "矮人"]

listbox_data = ["阿洛伊斯王国", "西里尔公国", "卡马利", "三石部落", "银箭兄弟会",
                "恶疫谷", "伊拉米尔", "神罚领", "叛木者要塞", "深翠盆地"]


class MyApp(Taro.App):

    def run(self):
        # 初始化窗口
        window = Window(height=27, width=64, title="所有控件")
        window.layout = LinearLayout(lines=4)

        # 初始化上方面板
        canvas_a = Canvas(fixed=False)
        canvas_a.layout = GridLayout(lines=1, columns=3)

        # 初始化多选框
        checkbox = CheckBox(width=20, height=8, title="多选框", border=Canvas.BD_STANDARD)
        checkbox.layout = LinearLayout(filled=True)
        for i in range(6):
            checkbox.additem(checkbox_data[i])

        # 初始化单选框
        radiobox = RadioBox(width=20, height=8, title="单选框", border=Canvas.BD_STANDARD, fixed=True)
        radiobox.layout = LinearLayout(filled=True)
        for i in range(3):
            radiobox.additem(radiobox_data[i])

        # 初始化列表
        listbox = ListBox(width=20, height=8)
        for i in range(10):
            listbox.additem(listbox_data[i])

        canvas_a.add(checkbox)
        canvas_a.add(radiobox)
        canvas_a.add(listbox)

        # 初始化中央面板
        canvas_b = Canvas(height=4, width=window.iwidth, title="下拉框", border=Canvas.BD_STANDARD)

        # 初始化下拉框
        combo_a = ComboBox(width=20)
        for item in combo_data.keys():
            combo_a.additem(item)
        combo_b = ComboBox(width=20)

        canvas_b.add(Label(text="物品类别："))
        canvas_b.add(Label(text="物品名称："), pos_y=1)
        canvas_b.add(combo_a, pos_x=10)
        canvas_b.add(combo_b, pos_y=1, pos_x=10)

        # 初始化标签页面板
        tabgroup = TabGroup(height=10, width=60)

        canvas_tab_a = Canvas(height=tabgroup.iheight, width=tabgroup.iwidth)
        canvas_tab_b = Canvas(height=tabgroup.iheight, width=tabgroup.iwidth)
        canvas_tab_c = Canvas(height=tabgroup.iheight, width=tabgroup.iwidth)

        canvas_tab_a.add(Label(text=words_a))
        canvas_tab_b.add(Label(text=words_b))
        canvas_tab_c.add(Label(text=words_c))

        tabgroup.addcanvas("骑士", canvas_tab_a)
        tabgroup.addcanvas("死灵法师", canvas_tab_b)
        tabgroup.addcanvas("恶堕之子", canvas_tab_c)

        window.add(canvas_a)
        window.add(canvas_b)
        window.add(tabgroup)

        # 添加下拉框联动事件
        def combo_changed():
            combo_b.clearitems()
            for item in combo_data[combo_a.selected.text]:
                combo_b.additem(item)

        combo_a.selected_item_changed = combo_changed
        window.closed = lambda evt: Taro.shutdown()


if __name__ == "__main__":
    Taro.runapp(MyApp)
