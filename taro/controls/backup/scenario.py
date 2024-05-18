# -- coding: utf-8 --
from __future__ import division

import time
import curses

from proj import options

from proj.core.map import Terran
from proj.core.map import HexMap

from proj.ui.terminal.strutils import Colored
from proj.ui.terminal.strutils import strwidth
from proj.ui.terminal.strutils import fixed
from proj.ui.terminal.common import UIControl
from proj.ui.terminal.text import Text
from proj.ui.terminal.dialog import Dialog
from proj.ui.terminal.scrolled import Scrolled
from proj.ui.terminal.infodialog import InfoDialog

from proj.data import assets


GWIDTH = 11
GHEIGHT = 4

HOR = "-"

VER = "|"


def vision(obj, asset, thumbnail=False):
    vision_d = {"fcolor": "white", "bcolor": "black", "attrs": []}
    if options.USE_FULL_WIDTH_FONT:
        vision = asset["vision_half"]
    else:
        vision = asset["vision_full"]
    if "effects" in vision:
        vision_d.update(vision["effects"])
    if thumbnail and "thumbnail" in vision:
        character = vision["thumbnail"]
    else:
        character = vision["character"] 
    return character, vision_d


class ScenarioGrid(UIControl):

    def initialize(self, terran, building=None, entity=None, title=None):
        self.terran = terran
        self.building = building
        self.entity = entity
        if title is not None:
            self.title = Text(content=title)
            self.add(self.title)
        elif self.building is not None:
            self.title = Text(content=self.building.name)
            self.add(self.title)
        else:
            self.title = None
        self.selected = False

    def paint(self):
        self.cursor.reset()
        if self.building is not None:
            asset = getattr(assets, "%s_VISION" % self.building.id)
            grid_char, grid_vision = vision(self.building, asset)
        elif self.terran is not None:
            asset = getattr(assets, "%s_VISION" % self.terran.id)
            grid_char, grid_vision = vision(self.terran, asset)
        else:
            grid_char = " "
            grid_vision = {}
        char_len = strwidth(grid_char)
        if self.selected:
            self.cursor.text(grid_char * (self.width * self.height // char_len), 
                             fcolor="black", bcolor="white", attrs=["bold"])
        else:
            self.cursor.text(grid_char * (self.width * self.height // char_len), **grid_vision)


class Scenario(UIControl):
    """
    地图封装控件
    """
    def initialize(self, map, gwidth=None, gheight=None):
        self.map = map
        if gwidth is None:
            self.gwidth = GWIDTH
        else:
            self.gwidth = gwidth
        if gheight is None:
            self.gheight = GHEIGHT
        else:
            self.gheight = gheight

        self.window_height = options.CAMERA_WINDOW_HEIGHT
        self.window_width = options.CAMERA_WINDOW_WIDTH

        self.entities = None
        self.coordinates = None
        self.show_trace = False
        self.selected = (0, 0)

        window = HexMap.window(self.map, 0, 0, self.window_height, self.window_width)
        for index in range(self.window_height * self.window_width):
            i = index % self.window_width
            j = index // self.window_width
            pos_y = 1 + j * (self.gheight + 1)
            pos_x = 1 + i * (self.gwidth + 1)
            if j % 2 == 1:
                pos_x += self.gwidth // 2 
            unit = window.grid(j, i)
            grid = ScenarioGrid(pos_y=pos_y, pos_x=pos_x, height=self.gheight, width=self.gwidth, 
                terran=unit.terran, building=unit.building, title=unit.title)
            self.add(grid)

        self.grid(0, 0).selected = True

    def paint(self):
        self.lines()

    def grid(self, y, x):
        return self.children[self.window_width * y + x]

    def lines(self):
        hline = "-" * (self.window_width * (self.gwidth + 1) + self.gwidth // 2)
        vline = "|" + (" " * self.gwidth + "|") * self.window_width
        for j in range(self.window_height * (self.gheight + 1)):
            if j % (self.gheight + 1) == 0:
                self.cursor.textline(hline)
            elif j // (self.gheight + 1) % 2 == 0:
                self.cursor.textline(vline)
            elif j // (self.gheight + 1) % 2 == 1:
                self.cursor.textline(" " * (self.gwidth // 2) + vline)
        self.cursor.textline(hline)

    def select(self, y, x):
        grid = self.grid(y, x)
        grid.selected = True
        grid.painted = False

    def unselect(self, y, x):
        grid = self.grid(y, x)
        grid.selected = False
        grid.painted = False

    def handle(self, key):
        if key == options.KEY_UP:
            self.unselect(*self.selected)
            self.selected = (self.selected[0] - 1, self.selected[1])
            self.select(*self.selected)
        elif key == options.KEY_LEFT:
            self.unselect(*self.selected)
            self.selected = (self.selected[0], self.selected[1] - 1)
            self.select(*self.selected)
        elif key == options.KEY_DOWN:
            self.unselect(*self.selected)
            self.selected = (self.selected[0] + 1, self.selected[1])
            self.select(*self.selected)
        elif key == options.KEY_RIGHT:
            self.unselect(*self.selected)
            self.selected = (self.selected[0], self.selected[1] + 1)
            self.select(*self.selected)
        elif key == options.KEY_D:
            self.help(self.selected)
        elif key == options.KEY_THUMBNAIL:
            self.thumbnail()

    def help(self, ac):
        self.active = False
        grid = self.grid(*self.selected)
        pos_y = grid.pos_y + grid.height // 2
        pos_x = grid.pos_x + grid.width // 2
        mgrid = self.map.grid(*self.selected)
        dialog = InfoDialog(pos_y=pos_y, pos_x=pos_x, 
                     zindex=self.zindex + 1, obj=mgrid)
        dialog.render()
        dialog.listen()
        self.active = True

    def thumbnail(self):
        self.active = False
        pos_y, pos_x, height, width = self.thumbsize()
        thumb = Dialog(pos_y=pos_y, pos_x=pos_x, height=height, width=width, 
                       zindex=self.zindex + 1, title=self.map.name, 
                       substance=Scrolled(substance=MapThumbnail(map=self.map)),
                       fixed=True)
        thumb.render()
        thumb.listen()
        self.active = True

    def thumbsize(self):
        height = int(curses.LINES * 0.85)
        width = int(curses.COLS * 0.6)
        pos_y = int(0.5 * (curses.LINES - height))
        pos_x = int(0.5 * (curses.COLS - width))
        return pos_y, pos_x, height, width


class MapThumbnail(UIControl):

    def initialize(self, map):
        self.map = map
        self.gwidth = 2
        self.entities = None
        self.resize(self.map.height, self.map.width * self.gwidth + self.gwidth // 2)

    def colorvision(self, pt):
        if pt.building is not None:
            asset = getattr(assets, "%s_VISION" % pt.building.id)
            return vision(pt.building, asset, True)
        elif pt.terran is not None:
            asset = getattr(assets, "%s_VISION" % pt.terran.id)
            return vision(pt.terran, asset, True)
        else:
            return " ", {}

    def paint(self):
        """
        对略缩图渲染速率进行少量优化
        """
        #t1 = time.time()
        self.cursor.reset()
        if self.entities is None:
            self.entities = []
        entity_info = {}
        for p in self.entities:
            loc = p["location"]
            entity_info[loc] = p
        plines = []
        for j in range(self.map.height):
            content_line = (self.gwidth // 2) * (j % 2) * " "
            fix_count = 0
            last_g = None
            last_content = None
            for i in range(self.map.width):
                g = self.map.grid(j, i)
                content = ""
                if len(content) == 0 and (i, j) in entity_info:
                    if not entity_info[(i, j)]["player"]:
                        content += Colored("P", color="cyan", attrs=["bold"])
                    else:
                        content += Colored("P", color="red", attrs=["bold"])
                elif len(content) == 0 and g.building is not None:
                    building_char, building_color = self.colorvision(g)
                    content += Colored(building_char, **building_color)
                elif (i, j) in self.map.entries:
                    if self.map.entries[(i, j)] == "MAP_WORLD":
                        content += Colored("出", bcolor="cyan")
                    else:
                        content += Colored("场", bcolor="cyan")
                if last_g is not None:
                    if content != last_content or g.building is not None or \
                       g.terran != last_g.terran or (i, j) in self.map.entries:
                        terran_char, terran_color = self.colorvision(last_g)
                        content_line += fixed(self.gwidth * fix_count, n=last_content, 
                                                 bg=terran_char, **terran_color)
                        fix_count = 0
                fix_count += 1
                last_g = g
                last_content = content
            terran_char, terran_color = self.colorvision(last_g)
            content_line += fixed(self.gwidth * fix_count, n=last_content, 
                                     bg=terran_char, **terran_color)
            content_line += fixed((self.gwidth // 2) * ((j + 1) % 2), bg=" ")
            plines.append(content_line)
        for pl in plines:
            self.cursor.colorline(pl)
