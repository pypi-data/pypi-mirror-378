"""
Frame dumper: writes PNG files (zero-deps) from software renderer frames.
"""
from __future__ import annotations
from lygui.core import NewFrame, Render
from lygui.renderers.software import create_framebuffer, fill_rect, draw_label
from lygui.utils.color import rgba
import os, struct, zlib

def run(ui_callable, frames=60, fps=60, size=(960,600), out_dir="out_frames", make_gif=False, gif_name="demo.gif"):
    os.makedirs(out_dir, exist_ok=True)
    w, h = size
    for i in range(max(1, frames)):
        NewFrame()
        ui_callable()
        cmds = Render()
        fb = create_framebuffer(w, h, rgba(220,221,225,255))
        _execute(cmds, fb, w, h)
        path = os.path.join(out_dir, f"frame_{i:04d}.png")
        write_png_rgba(path, fb, w, h)

def _execute(cmds, fb, w, h):
    # same as preview; duplicated to keep outputs independent
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

def write_png_rgba(path, pixels, w, h):
    # PNG RGBA8 writer (zero-deps)
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag+data) & 0xffffffff)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)  # 8-bit, color type 6 (RGBA)
    # Add filter byte 0 for each row
    raw = bytearray()
    stride = w*4
    for y in range(h):
        raw.append(0)
        start = y*stride
        raw.extend(pixels[start:start+stride])
    compressed = zlib.compress(bytes(raw), level=9)
    with open(path, "wb") as f:
        f.write(sig)
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", compressed))
        f.write(chunk(b"IEND", b""))