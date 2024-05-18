# -- coding: utf-8 --

from proj import options

from proj.core.map import MapGrid
from proj.core.item import Item

from proj.ui.terminal.common import UI
from proj.ui.terminal.strutils import Colored
from proj.ui.terminal.text import Text
from proj.ui.terminal.hypertext import HyperText
from proj.ui.terminal.scrolled import Scrolled
from proj.ui.terminal.dialog import Dialog


class InfoDialog(Dialog):

    height = 18
    width = 40

    def initialize(self, zindex=1, obj=None):
        if self.pos_y + self.height >= UI.ScreenHeight:
            self.pos_y -= self.height + 1
        if self.pos_x + self.width >= UI.ScreenWidth:
            self.pos_x -= self.width + 1
        texttype = InfoText.All[InfoText.fullname(obj.__class__)]
        title = "信息"
        super(InfoDialog, self).initialize(zindex=zindex,
            title=title, substance=Scrolled(substance=texttype(obj=obj)), 
            fixed=True)


class InfoText(HyperText):

    All = {}

    height = 14
    width = 36

    @staticmethod
    def fullname(klass):
        if klass.__module__ == "builtins":
            return klass.__name__
        else:
            return ".".join([klass.__module__, klass.__name__])

    def initialize(self, obj):
        super(InfoText, self).initialize()
        self.types = {}
        self.textualize(obj)

    def textualize(self, obj):
        return None

    def handle(self, key):
        ret = super(InfoText, self).handle(key)
        if ret:
            return ret
        if key == options.KEY_D:
            if self.selected == (-1, -1):
                return False
            self.info()
            return True
           
    def info(self):
        self.active = False
        pos_y = self.abs_y + self.selected[0] + 1
        pos_x = self.abs_x + self.selected[1] + 1
        obj = self.types[self.selected] 
        dialog = InfoDialog(pos_y=pos_y, pos_x=pos_x, zindex=2, obj=obj)
        dialog.render()
        dialog.listen()
        self.active = True


def bindmodel(*klass):
    def _bindmodel(cls):
        for kls in klass:
            InfoText.All[InfoText.fullname(kls)] = cls
        return cls
    return _bindmodel


@bindmodel(MapGrid)
class MapGridInfoText(InfoText):

    def textualize(self, obj):
        map = obj.map
        pos_y = obj.y
        pos_x = obj.x
        content = []
        grid = obj
        self.content = ["场景：%s" % map.name,
                        "坐标：（%s，%s）" % (pos_x, pos_y),
                        "地形：%s" % grid.terran.name,
                        "所有者：无",
                        "",
                        "采集项：" + Colored("甘草", fcolor="green", attrs=["bold"]) + \
                        "、" + Colored("玄铁", fcolor="magenta", attrs=["bold"]) + \
                        "、？？",
                        "",
                        "存在单位：无           ",
                        "存在建筑：无           "]

        self.hypers[(5, 8)] = Colored("甘草", fcolor="green", attrs=["bold"])
        self.hypers[(5, 14)] = Colored("玄铁", fcolor="magenta", attrs=["bold"])
        self.types[(5, 8)] = Item()
        self.types[(5, 14)] = Item()


@bindmodel(Item)
class ItemInfoText(InfoText):

    def textualize(self, obj):
        if self.selected == (5, 12):
            content = [Colored("甘草", fcolor="green", attrs=["bold"]),
                       "",
                       "标签：草药、材料",
                       "简介：常见的草药，性味甘平，常用于", 
                       "      解毒。"]
        elif self.selected == (5, 18):
            content = [Colored("玄铁", fcolor="magenta", attrs=["bold"]),
                       "",
                       "标签：矿石、材料",
                       "简介：极为罕见的矿物，颜色如墨，质", 
                       "      地坚硬。相传武器中只要用上一",
                       "      点便可削铁如泥。"]
        else:
            return
        self.active = False
        pos_y = self.abs_y + self.selected[0] + 1
        pos_x = self.abs_x + self.selected[1] + 1
        dialog = InfoDialog(pos_y=pos_y, pos_x=pos_x, zindex=2, title="物品信息",
                     substance=Scrolled(substance=Text(height=self.height, width=self.width, content=content)))
        dialog.render()
        dialog.listen()
        self.active = True
