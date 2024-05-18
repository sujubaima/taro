import logging
import queue


LOG = logging.getLogger()


class UIEvent(object):
    """
    转换curses键盘以及鼠标事件
    """
    Queue = queue.Queue()

    always = False
    object = None


class KeyInput(UIEvent):

    def __init__(self, key):
        super(KeyInput, self).__init__()
        self.key = key


class MouseEvent(UIEvent):

    def __init__(self, pos_y, pos_x):
        super(MouseEvent, self).__init__()
        self.pos_y = pos_y
        self.pos_x = pos_x


class MouseLeftClicked(MouseEvent):
    pass


class MouseLeftDoubleClicked(MouseEvent):
    pass


class MouseLeftPressed(MouseEvent):
    pass


class MouseLeftReleased(MouseEvent):
    pass


class MouseRightClicked(MouseEvent):
    pass


class MouseRightDoubleClicked(MouseEvent):
    pass


class MouseRightPressed(MouseEvent):
    pass


class MouseRightReleased(MouseEvent):
    pass


class MouseScrollUp(MouseEvent):
    pass


class MouseScrollDown(MouseEvent):
    pass
