#!/usr/bin/env python3
"""把 claude 套在一个伪终端里跑，它画吉祥物螃蟹的那三行在半路换成一只猫。

    python3 ~/.claude/kecat.py [claude 的参数…]     # .bashrc 里的 claude() 会走这里

螃蟹是 Claude Code 自己用方块字拼的（3 行 × 9 格，源码里叫 clawd）。这里不碰它的程序，
只认它吐出来的那几段字、换成同宽的颜文字猫（粗体莓粉）。

⚠ 必须配合 prefersReducedMotion=true（.bashrc 里一起传）：螃蟹被点或者启动时会跳/左看右看，
  那时渲染器只重画变了的那几格，碎片认不出来＝猫身上露出半只螃蟹。关了动效它就一直是正面那一帧。
⚠ Claude Code 升级后要是又见到螃蟹，多半是它换了拼法：抓一下原始输出
  （tmux pipe-pane -o），对照下面 ROW* 三条改。
"""
import errno
import fcntl
import os
import pty
import re
import select
import signal
import struct
import sys
import termios
import time
import tty

E = rb'((?:\x1b\[[0-9;:?<>=]*[ -/]*[@-~])*)'      # 夹在几段之间的颜色/背景转义，原样保留
U = lambda s: s.encode()

# 普通字符拼的颜文字、粗体莓粉。
#     螃蟹（正面）               猫（每行宽度跟螃蟹那行一样，后面的字才不会挪位）
#  ' ▐' '▛███▛█'             '  /\\_/\\ '
#  '▝▜' '█████' '█▀'         ' ( •ω• ) '
#  '  ▝▝ ▝▝  '               ' / >♡    '
# 换的时候把它原来那几段颜色/背景转义**挪到猫后面**再吐：渲染器以为此刻还是螃蟹那套颜色，状态得对得上。
CAT = ('  /\\_/\\ ', ' ( •ω• ) ', ' / >♡    ')
PINK = b'\x1b[1;38;2;196;74;110m' if os.environ.get('COLORTERM') in ('truecolor', '24bit') else b'\x1b[1;38;5;168m'


def paint(text, *esc):
    return PINK + text.encode() + b'\x1b[22m' + b''.join(e or b'' for e in esc)


ROW1 = (re.compile(rb'( ?)' + U('▐') + E + U('▛███▛█')),
        lambda m: paint(CAT[0][0 if m.group(1) else 1:8], m.group(2)))
ROW2 = (re.compile(U('▝▜') + E + U('█████') + E + U('█▀')),
        lambda m: paint(CAT[1], m.group(1), m.group(2)))
ROW3 = (re.compile(U('  ▝▝ ▝▝  ') + rb'|' + U('▝▝ ▝▝')),
        lambda m: paint(CAT[2] if len(m.group(0)) > len(U('▝▝ ▝▝')) else CAT[2][2:7]))
RULES = (ROW1, ROW2, ROW3)

HOLD = 64          # 末尾这么多字节里有方块字就先压住，等下一块拼上再换（螃蟹可能被切在两次 read 中间）
HOLD_MS = 15


def swap(b):
    for rx, fn in RULES:
        b = rx.sub(fn, b)
    return b


def winsize(src, dst):
    try:
        fcntl.ioctl(dst, termios.TIOCSWINSZ, fcntl.ioctl(src, termios.TIOCGWINSZ, b'\0' * 8))
    except OSError:
        pass


def main():
    args = ['claude'] + sys.argv[1:]
    if not (os.isatty(0) and os.isatty(1)):
        os.execvp('claude', args)
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp('claude', args)
    winsize(1, fd)
    signal.signal(signal.SIGWINCH, lambda *a: (winsize(1, fd), os.kill(pid, signal.SIGWINCH)))
    old = termios.tcgetattr(0)
    tty.setraw(0)
    pend, since = b'', 0.0
    try:
        while True:
            tmo = None
            if pend:
                tmo = max(0.0, since + HOLD_MS / 1000 - time.monotonic())
            try:
                r, _, _ = select.select([0, fd], [], [], tmo)
            except InterruptedError:
                continue
            if 0 in r:
                d = os.read(0, 65536)
                if not d:
                    break
                os.write(fd, d)
            if fd in r:
                try:
                    d = os.read(fd, 65536)
                except OSError as e:
                    if e.errno == errno.EIO:
                        d = b''
                    else:
                        raise
                if not d:
                    if pend:
                        os.write(1, swap(pend))
                    break
                if not pend:
                    since = time.monotonic()
                pend += d
            if not pend:
                continue
            out = swap(pend)
            tail = out[-HOLD:]
            if b'\xe2\x96' in tail and time.monotonic() - since < HOLD_MS / 1000:
                cut = len(out) - HOLD + tail.find(b'\xe2\x96')
                cut = max(cut, 0)
                # 留着的这截下次还要跟新来的拼起来再认一遍，所以留的是**换过之后**的字节——换过的猫不会再被认成螃蟹
                os.write(1, out[:cut])
                pend = out[cut:]
            else:
                os.write(1, out)
                pend = b''
    finally:
        termios.tcsetattr(0, termios.TCSAFLUSH, old)
    _, st = os.waitpid(pid, 0)
    sys.exit(os.waitstatus_to_exitcode(st) if hasattr(os, 'waitstatus_to_exitcode') else 0)


if __name__ == '__main__':
    main()
