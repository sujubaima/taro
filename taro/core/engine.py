# -- coding: utf-8 --
import os
import sys
import traceback
import time
import threading
#import readline

import curses

from taro import options
from taro.utils import log

from taro.core.event import *
from taro.core.ui import UIEvent
from taro.core.ui import UI


LOG = None

os.environ["TERM"] = "xterm-1006"


class InputThread(threading.Thread):

    MouseMap = {
      curses.BUTTON1_PRESSED: MouseLeftPressed,
      curses.BUTTON1_RELEASED: MouseLeftReleased,
      curses.BUTTON1_CLICKED: MouseLeftClicked,
      curses.BUTTON1_DOUBLE_CLICKED: MouseLeftDoubleClicked,
      curses.BUTTON3_PRESSED: MouseRightPressed,
      curses.BUTTON3_RELEASED: MouseRightReleased,
      curses.BUTTON3_CLICKED: MouseRightClicked,
      curses.BUTTON3_DOUBLE_CLICKED: MouseRightDoubleClicked,
      curses.BUTTON4_PRESSED: MouseScrollUp,
      curses.BUTTON2_PRESSED: MouseScrollDown,
      # 滚轮下滑有特殊键值
      134217728: MouseScrollDown,
      2097152: MouseScrollDown
    }

    def __init__(self, *args, **kwargs):
        super(InputThread, self).__init__(*args, **kwargs)
        self.stopped = False

    def get(self):
        key = UI.Root.cursor.cswin_.getch()
        return self.transfer(key)

    def transfer(self, key):
        if key is None or key == curses.ERR:
            return None
        if key == curses.KEY_MOUSE:
            try:
                _, x, y, _, state = curses.getmouse()
            except Exception as e:
                return None
            mousetype = InputThread.MouseMap.get(state)
            if mousetype is None:
                return None
            return mousetype(y, x)
        else:
            return KeyInput(key)

    def _run(self):
        while not self.stopped:
            evt = self.get()
            if evt is None:
                continue
            UIEvent.Queue.put(evt)

    def run(self):
        UIEngine.execute(self._run)

    def stop(self):
        self.stopped = True


class EventThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(EventThread, self).__init__(*args, **kwargs)
        self.stopped = False

    def _run(self):
        while not self.stopped:
            try:
                evt = UIEvent.Queue.get(timeout=1)
            except Exception as e:
                continue
            if evt.object is not None:
                evt.object.handle(evt)
            else:
                ctrl_list = []
                stack = [UI.Root]
                while len(stack) > 0:
                    ctrl = stack.pop(0)
                    #if ctrl.cursor is not None and ctrl.active:
                    #    ctrl_list.append(ctrl)
                    #if ctrl.cursor is not None and not ctrl.active:
                    #    continue
                    if ctrl.cursor is not None:
                        if evt.always:
                            ctrl_list.append(ctrl)
                        elif ctrl.active:
                            ctrl_list.append(ctrl)
                        else:
                            continue
                    for child in ctrl.children[::-1]: #sorted(ctrl.children, key=lambda x: x.zindex):
                        stack.append(child)
                for control in ctrl_list[::-1]:
                    control.handle(evt)

    def run(self):
        UIEngine.execute(self._run)

    def stop(self):
        self.stopped = True


class RenderThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(RenderThread, self).__init__(*args, **kwargs)
        self.stopped = False

    def _run(self):
        ts_last = time.time()
        while not self.stopped:
            #curses.curs_set(0)
            UI.renderall()
            if UI.Focused is not None:
                cursor_y = UI.Focused.abs_y + UI.Focused.cursor.pos_y
                cursor_x = UI.Focused.abs_x + UI.Focused.cursor.pos_x
                curses.setsyx(cursor_y, cursor_x)
                curses.curs_set(1)
            else:
                curses.curs_set(0)
            ts_now = time.time()
            slp_time = ts_last + options.RENDER_INTERVAL - ts_now
            if slp_time > 0:
                time.sleep(slp_time)
            ts_last = time.time()

    def run(self):
        UIEngine.execute(self._run)

    def stop(self):
        self.stopped = True


class UIEngine(object):
    
    RenderThread = None
    EventThread = None
    InputThread = None

    class App(object):

        def run(self):
            pass

    @staticmethod
    def config(key, value):
        setattr(options, key, value)

    @staticmethod
    def runapp(app):
        global LOG
        exc = None
        LOG = log.init_logger()
        LOG.info("Engine starts!")
        try:
            UIEngine.init()
            app().run()
            UIEngine.RenderThread.join()
            UIEngine.EventThread.join()
            UIEngine.InputThread.join()
        except Exception as e:
            exc = sys.exc_info()
        finally:
            curses.endwin()
            if exc is not None:
                #traceback.print_exception(*exc)
                LOG.error("".join(traceback.format_exception(*exc)))
                time.sleep(5)
            curses.endwin()
            UIEngine.shutdown()

    @staticmethod
    def init():
        scr = curses.initscr()
        curses.cbreak()
        curses.noecho()
        curses.halfdelay(1)
        curses.curs_set(0)
        #curses.mousemask(-1)
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
        curses.start_color()
        #curses.init_color(99, 255, 50, 150)
        scr.keypad(1)
        #scr.nodelay(True)

        UI.ScreenHeight = curses.LINES
        UI.ScreenWidth = curses.COLS
        UI.Root = UI(height=UI.ScreenHeight, width=UI.ScreenWidth)
        #UI.Root.cswin_ = scr

        UIEngine.RenderThread = RenderThread()
        UIEngine.EventThread = EventThread()
        UIEngine.InputThread = InputThread()
        UIEngine.RenderThread.start()
        UIEngine.EventThread.start()
        UIEngine.InputThread.start()

    @staticmethod
    def execute(func, *args, **kwargs):
        exc = None
        try:
            func(*args, **kwargs)
        except Exception as e:
            exc = sys.exc_info()
        finally:
            curses.endwin()
            if exc is not None:
                traceback.print_exception(*exc)
                LOG.exception(exc)

    @staticmethod
    def shutdown():
        LOG.info("Engine shuts down!")
        UIEngine.RenderThread.stop()
        UIEngine.EventThread.stop()
        UIEngine.InputThread.stop()
        #UIEngine.RenderThread.join()
        #UIEngine.EventThread.join()


Taro = UIEngine


if __name__ == "__main__":
    buffer = UIBuffer()
    buffer.move(9, 2)
    buffer.echo("hahahah")
    for line in buffer.lines():
        print(line)
