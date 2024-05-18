# -- coding: utf-8 --

import sys
import re

from taro import options


UNICODE_WIDTH = [
    (126, 1), (159, 0), (687, 1), (710, 0), (711, 1),
    (727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
    (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1),
    (8426, 0), (9000, 1), (9002, 2), (11021, 1), (12350, 2),
    (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1),
    (55203, 2), (63743, 1), (64106, 2), (65039, 1), (65059, 0),
    (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
    (120831, 1), (262141, 2), (1114109, 1),
]


WINDOWS_CHARS = set([215, 923, 936, 966, 1044, 1051, 1078, 8593, 8595, 8592,
                     8594, 8598, 8599, 8601, 8600,
                     8730, 8741, 8745, 8978, 9532, 9660, 9675, 9679])


if sys.version_info.major != 2:
    unicoded = lambda x, coding="utf-8": x
else:
    unicoded = lambda x, coding="utf-8": x.decode(coding)


def charwidth(o):
    """
    用于计算字符的显示宽度，仅支持UTF-8
    """
    if o in WINDOWS_CHARS and options.USE_FULL_WIDTH_FONT:
        return 2
    if o == 0xe or o == 0xf:
        return 0
    for num, wid in UNICODE_WIDTH:
        if o <= num:
            return wid
    return 1


def strwidth(word):
    """
    用于计算字符串的显示宽度，仅支持UTF-8
    """
    if isinstance(word, Colored):
        tword = "".join([st[0] for st in word.strlist])
    else:
        tword = re.sub("\033\[[0-9]+m", "", word)
    # charwidth这个方法暂时来看是最准的
    l = 0
    for o in unicoded(tword):
        l += charwidth(ord(o))
    return l


def fixed(width, n="", bg=" ", fcolor=None, bcolor=None, attrs=None):
    bg_d = (width - strwidth(n)) // strwidth(bg)
    bg_m = (width - strwidth(n)) % strwidth(bg)
    return n + Colored(" " * bg_m + bg * bg_d, fcolor=fcolor, bcolor=bcolor, attrs=attrs)


def align_center(content, fullsize):
    width = strwidth(content)
    if width > fullsize:
        return content
    left = (fullsize - width) // 2
    right = fullsize - left - width
    return " " * left + content + " " * right


def align_left(content, fullsize):
    width = strwidth(content)
    if width > fullsize:
        return content
    return content + " " * (fullsize - width)


def align_right(content, fullsize):
    width = strwidth(content)
    if width > fullsize:
        return content
    return " " * (fullsize - width) + content


class Colored(object):
    """
    用来适配正常显示与curses显示
    """
    def __init__(self, text="", fcolor=None, bcolor=None, attrs=None):
        self.strlist = []
        if isinstance(text, Colored):
            for st in text.strlist:
                self.strlist.append(st)
        else:
            strdict = self.makedict(text, fcolor, bcolor, attrs)
            self.strlist.append(strdict)

    def makedict(self, text="", fcolor=None, bcolor=None, attrs=None):
        if fcolor is None:
            fcolor = "white"
        if bcolor is None:
            bcolor = "black"
        if attrs is None:
            attrs = []
        return [text, fcolor, bcolor, attrs]

    def split(self, delim=" "):
        ret = []
        for piece in self.strlist:
            txt = piece[0]
            tsplit = txt.split(delim)
            for idx, t in enumerate(tsplit):
                clr = Colored(t, fcolor=piece[1], bcolor=piece[2], attrs=piece[3])
                if idx == 0 and len(ret) > 0:
                    ret[-1] += clr
                else:
                    ret.append(clr)
        return ret

    def rearrange(self, width):
        count = 0
        for piece in self.strlist:
            idx = 0
            while True:
                if idx >= len(piece[0]):
                    break
                p = piece[0][idx]
                if p == "\n":
                    count = 0
                    idx += 1
                    continue
                pwidth = strwidth(p)
                if count + pwidth >= width and idx != len(piece[0]) - 1:
                    piece[0] = piece[0][0:idx + 1] + "\n" + piece[0][idx + 1:]
                idx += 1
                count += pwidth
        return self

    def __str__(self):
        ret = ""
        for itm in self.strlist:
            ret += itm[0]
        return ret

    def __add__(self, other):
        if other is None:
            other = ""
        ret = Colored()
        for stri in self.strlist:
            ret.strlist.append(stri)
        if isinstance(other, Colored):
            tmp = other.strlist
        else:
            tmp = [self.makedict(other)]
        strl = ret.strlist[-1]
        strf = tmp[0]
        if strf[1] == strl[1] and \
           strf[2] == strl[2] and \
           strf[3] == strl[3]:
            ret.strlist[-1][0] = strl[0] + strf[0]
        else:
            ret.strlist.append(strf)
        for stri in tmp[1:]:
            ret.strlist.append(stri)
        return ret

    def __radd__(self, other):
        if other is None:
            other = ""
        ret = Colored()
        if isinstance(other, Colored):
            for stri in other.strlist:
                ret.strlist.append(stri)
        else:
            ret.strlist.append(self.makedict(other))
        strl = ret.strlist[-1]
        strf = self.strlist[0]
        if strf[1] == strl[1] and \
           strf[2] == strl[2] and \
           strf[3] == strl[3]:
            ret.strlist[-1][0] = strl[0] + strf[0]
            for stri in self.strlist[1:]:
                ret.strlist.append(stri)
        else:
            for stri in self.strlist:
                ret.strlist.append(stri)
        return ret

    def __mul__(self, other):
        ret = Colored()
        for i in range(other):
            ret = ret + self
        return ret

    def __rmul__(self, other):
        ret = Colored()
        for i in range(other):
            ret = self + ret
        return ret

    def __len__(self):
        ret = 0
        for strp in self.strlist:
            ret += len(strp[0])
        return ret

    @staticmethod
    def join(strlist, sep=""):
        ret = ""
        first = True
        for cs in strlist:
            if first:
                first = False
            else:
                ret += sep
            ret += cs
        return ret
