"""
Headless preview runner: steps frames and exercises UI/renderer without writing files.
"""
from __future__ import annotations
from lygui.core import NewFrame, Render
from lygui.renderers.software import create_framebuffer, fill_rect, draw_label
from lygui.utils.color import rgba

def run(ui_callable, frames=60, fps=60, size=(960, 600)):
    w, h = size
    for _ in range(max(1, frames)):
        NewFrame()
        ui_callable()
        cmds = Render()
        # naive render to ensure pipeline works:
        fb = create_framebuffer(w, h, rgba(220,221,225,255))
        _execute(cmds, fb, w, h)
        # No display/output; useful for correctness checks and perf sampling

def _execute(cmds, fb, w, h):
    # minimal interpreter for a subset
    for cmd, args, kwargs in cmds:
        if cmd == "BeginWindow":
            name, (x,y), (ww,hh), flags = args
            fill_rect(fb, w, x, y, ww, hh, rgba(246,246,248,255))
            draw_label(fb, w, x+8, y+6, name, rgba(32,32,32,255))
        elif cmd == "Text":
            txt, (x,y) = args
            draw_label(fb, w, x, y, txt, rgba(24,24,24,255))
        elif cmd == "Button":
            label, (x,y), (bw,bh), wid = args
            fill_rect(fb, w, x, y, bw, bh, rgba(236,236,236,255))
            draw_label(fb, w, x+6, y+8, label, rgba(10,10,10,255))
        elif cmd == "Checkbox":
            label, (x,y), value, wid = args
            fill_rect(fb, w, x, y, 18, 18, rgba(255,255,255,255))
            if value:
                # crude checkmark
                fill_rect(fb, w, x+3, y+9, 2, 2, rgba(30,136,229,255))
            draw_label(fb, w, x+24, y+1, label, rgba(10,10,10,255))
        elif cmd == "InputText":
            label, (x,y), width, value, wid = args
            draw_label(fb, w, x, y-16, label, rgba(10,10,10,255))
            fill_rect(fb, w, x, y, width, 22, rgba(255,255,255,255))
            draw_label(fb, w, x+6, y+3, str(value), rgba(10,10,10,255))
        elif cmd == "SliderFloat":
            label, (x,y), width, v, vmin, vmax, wid = args
            draw_label(fb, w, x, y-16, f"{label}: {v:.3f}", rgba(10,10,10,255))
            fill_rect(fb, w, x, y+8, width, 6, rgba(230,230,230,255))
            t = 0.0 if vmax==vmin else (v - vmin) / (vmax - vmin)
            kx = int(x + t * width)
            fill_rect(fb, w, kx-3, y+4, 6, 14, rgba(120,120,120,255))