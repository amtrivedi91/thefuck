import sys
import msvcrt
import colorama
import win_unicode_console
from .. import const


def init_output():
    win_unicode_console.enable()
    colorama.init()


def get_key():
    ch = msvcrt.getch()
    if ch in (b'\x00', b'\xe0'):  # arrow or function key prefix?
        ch = msvcrt.getch()  # second call returns the actual key code

    if ch == b'\x03':
        raise const.KEY_CTRL_C
    if ch == b'H':
        return const.KEY_UP
    if ch == b'P':
        return const.KEY_DOWN

    return ch.decode(sys.stdout.encoding)