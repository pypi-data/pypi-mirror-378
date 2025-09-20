"""
Zero-deps software renderer: rasterizes LyGui frame commands to an RGBA framebuffer.
"""
from __future__ import annotations
from typing import List, Tuple
import math

def create_framebuffer(w: int, h: int, color=(220,221,225,255)) -> List[int]:
    r,g,b,a = color
    pix = [0]*(w*h*4)
    for i in range(0, len(pix), 4):
        pix[i]=r; pix[i+1]=g; pix[i+2]=b; pix[i+3]=a
    return pix

def put_px(pix, w, x, y, rgba):
    if x<0 or y<0 or x>=w: return
    idx = (y*w + x)*4
    if idx<0 or idx+3>=len(pix): return
    r,g,b,a = rgba
    pix[idx]=r; pix[idx+1]=g; pix[idx+2]=b; pix[idx+3]=a

def fill_rect(pix, w, x, y, rw, rh, rgba):
    for yy in range(max(0,y), y+rh):
        base = yy*w*4 + max(0,x)*4
        end = min(w, x+rw)*4
        for i in range(base, yy*w*4 + end, 4):
            pix[i:i+4] = rgba

def draw_text(pix, w, x, y, text, rgba):
    # 5x7 bitmap font (ASCII 32..126)
    for i,ch in enumerate(text[:128]):
        cx = x + i*6
        draw_char(pix, w, cx, y, ch, rgba)

_font = {
    # digits 0-9 minimal
    '0':[" ### ",
         "#  ##",
         "# # #",
         "##  #",
         "#   #",
         "#   #",
         " ### "],
    '1':["  #  ",
         " ##  ",
         "  #  ",
         "  #  ",
         "  #  ",
         "  #  ",
         " ### "],
    '2':[" ### ",
         "#   #",
         "    #",
         "  ## ",
         " #   ",
         "#    ",
         "#####"],
    '3':["#### ",
         "    #",
         "   # ",
         "  ## ",
         "    #",
         "#   #",
         " ### "],
    '4':["   # ",
         "  ## ",
         " # # ",
         "#  # ",
         "#####",
         "   # ",
         "   # "],
    '5':["#####",
         "#    ",
         "#### ",
         "    #",
         "    #",
         "#   #",
         " ### "],
    '6':[" ### ",
         "#    ",
         "#    ",
         "#### ",
         "#   #",
         "#   #",
         " ### "],
    '7':["#####",
         "    #",
         "   # ",
         "  #  ",
         "  #  ",
         "  #  ",
         "  #  "],
    '8':[" ### ",
         "#   #",
         "#   #",
         " ### ",
         "#   #",
         "#   #",
         " ### "],
    '9':[" ### ",
         "#   #",
         "#   #",
         " ####",
         "    #",
         "    #",
         " ### "],
}
def _char_pattern(ch):
    if ch in _font: return _font[ch]
    # simple fallback: block
    return ["#####",
            "#   #",
            "#   #",
            "#   #",
            "#   #",
            "#   #",
            "#####"]

def draw_char(pix, w, x, y, ch, rgba):
    pat = _char_pattern(ch)
    for yy,row in enumerate(pat):
        for xx,c in enumerate(row):
            if c != ' ':
                put_px(pix, w, x+xx, y+yy, rgba)

def draw_label(pix, w, x, y, text, rgba):
    draw_text(pix, w, x, y, text, rgba)