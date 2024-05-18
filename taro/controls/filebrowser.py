import os
import time
import logging

from taro import options
from taro.utils.strutils import Colored
from taro.controls.button import Button
from taro.controls.window import Window
from taro.controls.listbox import ListBox
from taro.controls.label import Label
from taro.controls.inputbox import InputBox

LOG = logging.getLogger()


def size_format(size):
    unit = ["B", "KB", "MB", "GB"]
    tmp = size
    for i in range(len(unit)):
        if tmp < 1024:
            break
        if i != len(unit) - 1:
            tmp /= 1024
    return str(round(tmp, 2)) + unit[i]


class FileBrowser(Window):

    def setup(self, pwd=None, suffix=None, dir_enabled=False, writable=True, show_size=False, show_date=False):
        self.title = "文件浏览"
        super(FileBrowser, self).setup()
        self.listbox = ListBox(height=self.iheight - 3, width=self.iwidth)
        self.path_label = Label(text="文件名称：")
        self.path_input = InputBox(width=self.iwidth - self.path_label.width, active=writable)
        self.path_label.locate(self.iheight - 3)
        self.path_input.locate(self.iheight - 3, self.path_label.width)
        self.button_ok = Button(text="选择")
        self.button_cancel = Button(text="取消")
        self.button_ok.locate(self.iheight - 1)
        self.button_cancel.locate(self.iheight - 1, self.iwidth - self.button_cancel.width)
        self.button_ok.active = False
        self.add(self.listbox)
        self.add(self.path_label)
        self.add(self.path_input)
        self.add(self.button_ok)
        self.add(self.button_cancel)

        self.dir_enabled = dir_enabled
        self.show_size = show_size
        self.show_date = show_date

        self.pwd = pwd
        self.suffix = suffix
        self.path = None
        if self.pwd is not None:
            self._init_files()

        self.listbox.item_changed = lambda evt: self._selection_changed(evt)
        self.listbox.item_double_clicked = lambda evt: self._selection_double_clicked(evt)
        self.button_ok.clicked = lambda evt: self._file_opened(evt)

        self.selection_changed = lambda evt: None
        self.file_opened = lambda evt: None

    @property
    def writable(self):
        return self.path_input.active

    @writable.setter
    def writable(self, val):
        self.path_input.active = val

    def _init_files(self):
        self.path_input.text = ""
        for f in ["./", "../"]:
            fullpath = "%s/%s" % (self.pwd, f)
            text = Colored(f, fcolor="blue", attrs=["bold"])
            info = os.stat(fullpath)
            self.listbox.additem(text, binddata=(fullpath, info))
        dirs = []
        files = []
        for f in os.listdir(self.pwd):
            fullpath = "%s/%s" % (self.pwd, f)
            info = os.stat(fullpath)
            if os.path.isdir(fullpath):
                dirs.append(("./" + f + "/", fullpath, info))
            elif self.suffix is None or f.endswith(self.suffix):
                files.append((f, fullpath, info))
        for d in dirs:
            text = Colored(d[0], fcolor="blue", attrs=["bold"])
            self.listbox.additem(text, binddata=(d[1], d[2]))
        for f in files:
            fsize = size_format(f[2].st_size)
            mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(f[2].st_mtime))
            text = "./" + f[0]
            if self.show_size:
                fsize = size_format(f[2].st_size)
                text = "\n  %s" % fsize
            if self.show_date:
                mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(f[2].st_mtime))
                text += "\n  %s" % mtime
            self.listbox.additem(text, binddata=(f[1], f[2]))

    def _file_opened(self, evt):
        #fullpath = self.listbox.selected.binddata[0]
        fullpath = "%s/%s" % (self.pwd, self.path_input.text)
        self.path = fullpath
        self.file_opened(self, evt)

    def _selection_changed(self, evt):
        fullpath = self.listbox.selected.binddata[0]
        if self.listbox.selected is not None:
            self.button_ok.active = True
        elif os.path.isdir(fullpath) and not self.enabled_dir:
            self.button_ok.active = False
        else:
            self.button_ok.active = True
        self.path_input.text = self.listbox.selected.text
        self.selection_changed(self, evt)

    def _selection_double_clicked(self, evt):
        time.sleep(options.RENDER_INTERVAL)
        fullpath = self.listbox.selected.binddata[0]
        if os.path.isdir(fullpath):
            self.pwd = fullpath
            self.listbox.clearitems()
            self._init_files()
            self.button_ok.active = False
