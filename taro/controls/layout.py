import logging

from taro.core import UI
from taro.controls.canvas import Canvas


LOG = logging.getLogger()


class Layout(UI):

    control = None

    def setup(self):
        self.cursor = None

    def add(self, child, *args, **kwargs):
        super(Layout, self).add(child, *args, **kwargs)
        self.arrange()

    def remove(self, child, *args, **kwargs):
        super(Layout, self).remove(child, *args, **kwargs)
        self.arrange()

    def arrange(self):
        pass


class FillLayout(Layout):

    def arrange(self):
        if self.height != self.parent.iheight or self.width != self.parent.iwidth:
            self.resize(self.parent.iheight, self.parent.iwidth)
        for child in self.children:
            child.resize(self.height, self.width)


class FlowLayout(Layout):

    def arrange(self):
        child_pos_y = 0
        child_pos_x = 0
        for child in self.children:
            LOG.info(child)
            LOG.info("%s, %s, %s" % (child.width, child_pos_x, self.width))
            if child.width + child_pos_x > self.width:
                child_pos_x = 0
                child_pos_y += max([c.height for c in self.children])
            child.locate(child_pos_y, child_pos_x)
            child_pos_x += child.width


class LinearLayout(Layout):

    def setup(self, lines=1, filled=False):
        self.filled = filled
        super(LinearLayout, self).setup()
        self.lines = [None] * lines
        self._idx = 0

    def add(self, child, line=None):
        if line is None:
            line = self._idx
        else:
            self._idx = line
        if line >= len(self.lines):
            self.lines.extend([None] * (line - len(self.lines) + 1))
        self.lines[line] = child
        super(LinearLayout, self).add(child)
        #if self.filled:
        #    child.resize(width=self.width)
        self._idx += 1

    def remove(self, child, upmove=False):
        for idx, item in enumerate(self.lines):
            if item == child:
                break
        if upmove:
            for i in range(idx, len(self.lines)):
                self.lines[idx] = self.lines[idx + 1]
            self.lines.pop()
        else:
            self.lines[idx] = None
        super(LinearLayout, self).remove(child)

    def arrange(self):
        child_pos_y = 0
        for child in self.lines:
            if child is None:
                child_pos_y += 0
            else:
                child.locate(child_pos_y, 0)
                if self.filled:
                    child.resize(width=self.width)
                child_pos_y += child.height
        self.resize(height=child_pos_y)


class GridLayout(Layout):

    def setup(self, lines=1, columns=1, adjustable=True):
        super(GridLayout, self).setup()
        self.adjustable = adjustable
        self.lines = lines
        self.columns = columns
        self.grids = []
        for i in range(lines):
            self.grids.append([None] * columns)
        self._idx_line = 0
        self._idx_column = 0

    def add(self, child, line=None, column=None):
        if line is None:
            line = self._idx_line
        else:
            self._idx_line = line
        if column is None:
            column = self._idx_column
        else:
            self._idx_column = column
        self.grids[line][column] = child
        super(GridLayout, self).add(child)
        self._idx_column += 1
        if self._idx_column == self.columns:
            self._idx_column = 0
            self._idx_line += 1

    def arrange(self):
        if self.adjustable:
            self._arrange_adjustable()
        else:
            self._arrange_regular()

    def _arrange_regular(self):
        line_height = self.height // self.lines
        column_width = self.width // self.columns
        for i in range(0, self.lines):
            child_pos_y = line_height * i
            for j in range(0, self.columns):
                child_pos_x = column_width * j
                child = self.grids[i][j]
                if child is not None:
                    child.locate(child_pos_y, child_pos_x)

    def _arrange_adjustable(self):
        child_pos_y = [0] * self.lines
        child_pos_x = [0] * self.columns
        total_max_height = 0
        total_max_width = 0
        for i in range(0, self.lines):
            max_height = 0
            for child in self.grids[i]:
                if child is None:
                    max_height = max(max_height, 1)
                else:
                    max_height = max(max_height, child.height)
            total_max_height += max_height
            if i != self.lines - 1:
                child_pos_y[i + 1] = child_pos_y[i] + max_height
        for i in range(0, self.columns):
            max_width = 0
            for line in self.grids:
                child = line[i]
                if child is None:
                    max_width = max(max_width, 1)
                else:
                    max_width = max(max_width, child.width)
            total_max_width += max_width
            if i != self.columns - 1:
                child_pos_x[i + 1] = child_pos_x[i] + max_width
        for i in range(0, self.lines):
            for j in range(0, self.columns):
                child = self.grids[i][j]
                if child is not None:
                    child.locate(child_pos_y[i], child_pos_x[j])
        self.resize(total_max_height, total_max_width)
