#!/usr/bin/env python3
"""启动 claude 前：试着把终端底色换成奶油色，印一张小猫卡片。
stdout 只输出一个词：cream（终端认了换底色）/ plain（不认，别上浅色主题）。画面全写 /dev/tty。"""
import os, select, sys, termios, tty
CREAM = "f6e9d3"
def ask(fd, seq, wait=0.35):
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd); os.write(fd, seq); buf = b""
        while select.select([fd], [], [], wait)[0]:
            buf += os.read(fd, 256)
            if buf.endswith(b"\x07") or buf.endswith(b"\x1b\\"): break
        return buf.decode("latin1")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
try:
    fd = os.open("/dev/tty", os.O_RDWR)
except OSError:
    print("plain"); sys.exit()
os.write(fd, f"\033]11;#{CREAM}\007\033]10;#4a4038\007".encode())
r = ask(fd, b"\033]11;?\007").lower()
ok = f"rgb:{CREAM[0:2]*2}/{CREAM[2:4]*2}/{CREAM[4:6]*2}" in r or f"rgb:{CREAM[0:2]}/{CREAM[2:4]}/{CREAM[4:6]}" in r
if not ok:
    os.write(fd, b"\033]111\007\033]110\007")
P, G, D, Z = "\033[1;38;2;196;74;110m", "\033[38;2;98;120;70m", "\033[38;2;160;146;132m", "\033[0m"
card = f"""
{P}     /\\_/\\{Z}
{P}    ( •ω• ){Z}
{P}    / >♡    KeCode{Z}
{G}    cat cream terminal  ·  Claude Code{Z}
{D}    {'奶油底已铺好' if ok else '这个终端不让换底色，先用原来的配色'}{Z}

"""
os.write(fd, card.replace("\n", "\r\n").encode())
print("cream" if ok else "plain")
