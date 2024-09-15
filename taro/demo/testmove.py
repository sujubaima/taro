import curses

def main(win:curses.window):
    win.clear()
    win.nodelay(True)
    curses.mouseinterval(0)
    curses.mousemask(curses.REPORT_MOUSE_POSITION | curses.ALL_MOUSE_EVENTS)
    print('\033[?1003h') # enable mouse tracking with the XTERM API
    # https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Mouse-Tracking

    while True:
        ch=win.getch()
        if ch==curses.KEY_MOUSE:
            win.clear()
            _, x, y, _, bstate = curses.getmouse()
            win.addstr(0,0,str((x, y, bstate)))
            win.refresh()

curses.wrapper(main)
