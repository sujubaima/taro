import sys
import math
import time
import threading
import logging

from PIL import Image

from taro.core import UI
from taro.utils.strutils import Colored
from taro.controls.canvas import Canvas

LOG = logging.getLogger()

NCURSES_RGB = {
    #(0, 0, 0): {"fcolor": "black"},
    (0, 0, 0): {"fcolor": "white"},
    (0, 0, 160): {"fcolor": "blue"},
    (0, 160, 0): {"fcolor": "green"}, 
    (0, 160, 160): {"fcolor": "cyan"},
    (160, 0, 0): {"fcolor": "red"},
    (160, 0, 160): {"fcolor": "magenta"},
    (160, 80, 0): {"fcolor": "yellow"},
    #(160, 160, 160): {"fcolor": "white"},
    (160, 160, 160): {"fcolor": "black"},
    #(80, 80, 80): {"fcolor": "black", "attrs": ["bold"]},
    (80, 80, 80): {"fcolor": "white", "attrs": ["bold"]},
    (80, 80, 256): {"fcolor": "blue", "attrs": ["bold"]},
    (80, 256, 80): {"fcolor": "green", "attrs": ["bold"]},
    (80, 256, 256): {"fcolor": "cyan", "attrs": ["bold"]},
    (256, 80, 80): {"fcolor": "red", "attrs": ["bold"]},
    (256, 80, 256): {"fcolor": "magenta", "attrs": ["bold"]},
    (256, 256, 80): {"fcolor": "yellow", "attrs": ["bold"]},
    #(256, 256, 256): {"fcolor": "white", "attrs": ["bold"]}
    (256, 256, 256): {"fcolor": "black", "attrs": ["bold"]}
}

class ImageCanvas(Canvas):

    #CharDict = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")
    #CharDict = list("""@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`'. """)
    CharDict = list("MNHQ$OC67)oa+>!:+. ")
    #CharDict = list('@%MGal- ')
    #CharDict = ["~/. "]

    _imgsrc = None

    _pheight = 0
    _pwidth = 0

    def setup(self, colored=True, imgsrc=None, **kwargs):
        super(ImageCanvas, self).setup(**kwargs)

        self._img_lock = threading.Lock()
        self._buffer = []

        self.img_height = 1
        self.img_width = 1

        self._raw_imag = None
        self.img = None
        self.imgsrc = imgsrc

    @property
    def imgsrc(self):
        return self._imgsrc

    @imgsrc.setter
    def imgsrc(self, val):
        if self._imgsrc == val:
            return
        self._imgsrc = val
        self._raw_img = Image.open(self._imgsrc)
        #self.img = Image.open(self._imgsrc)
        self.imgsize()
        self._buffer = []
        self.flag.modified()

    def size_changed(self):
        if self.imgsrc is None:
            return
        self.imgsize()
        self._buffer = []
        self.flag.modified()

    def paint(self):
        self.cursor.reset()
        super(ImageCanvas, self).paint()
        if self.img is not None and len(self._buffer) == 0:
            self.img2char()
        self.cursor.move(self._pheight, 0)
        for l in self._buffer:
            self.cursor.move(x=self._pwidth)
            self.cursor.colorline(l)
            fd.write(str(l).replace(" ", "    ") + "\n")

    def imgsize(self):
        with self._img_lock:
            rw, rh = self._raw_img.size
            if rw / rh >= self.iwidth * 2 / self.iheight:
                self.img_height = self.iwidth * rh // rw // 2
                self.img_width = self.iwidth // 2
            else:
                self.img_height = self.iheight
                self.img_width = self.iheight * rw // rh
            if self.img_height != rh or self.img_width != rw:
                self.img = self._raw_img.resize((self.img_width, self.img_height), Image.NEAREST)
            else:
                self.img = self._raw_img
            self._pheight = (self.iheight - self.img_height) // 2
            self._pwidth = (self.iwidth - self.img_width * 2) // 2

    def get_char(self, r, g, b, alpha=256):
        if alpha == 0:
            return ' '
        length = len(ImageCanvas.CharDict)
        gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
        unit = (256.0 + 1) / length
        char = ImageCanvas.CharDict[int(gray / unit)]
        colorinfo = None
        delta = sys.maxsize
        for k, v in NCURSES_RGB.items():
            tmp = math.pow((r - k[0]), 2) + math.pow((g - k[1]), 2) + math.pow((b - k[2]), 2)
            if tmp < delta:
                delta = tmp
                colorinfo = v
        return char + " ", colorinfo

    def img2char(self):
        with self._img_lock:
            for i in range(self.img_height):
                line = ""
                for j in range(self.img_width):
                    text, colorinfo = self.get_char(*self.img.getpixel((j, i)))
                    line += Colored(text, **colorinfo)
                self._buffer.append(line)
