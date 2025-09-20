"""
Zero‑deps live viewer using the default web browser.
- Starts a tiny HTTP server (stdlib http.server)
- Renders frames in a background loop
- Serves / as HTML and /frame.png as the latest frame
No Tk/Qt/OS APIs are used. Cross‑platform as long as a browser exists.
"""
from __future__ import annotations
import threading, time, io, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

from lygui.core import NewFrame, Render
from lygui.renderers.software import create_framebuffer, fill_rect, draw_label
from lygui.utils.color import rgba
from lygui.outputs.framedump import write_png_rgba  # reuse internal PNG encoder

_HTML = b"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>LyGui Live</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
html,body{margin:0;background:#1f1f1f;color:#ddd;font-family:system-ui,Segoe UI,Roboto,Arial}
#wrap{display:flex;align-items:center;justify-content:center;height:100vh}
img{image-rendering:pixelated;max-width:96vw;max-height:92vh;box-shadow:0 10px 30px rgba(0,0,0,.5);border-radius:8px}
#hud{position:fixed;top:10px;left:10px;background:rgba(0,0,0,.45);padding:6px 10px;border-radius:6px;font-size:12px}
</style>
</head>
<body>
<div id="hud">LyGui Live (zero-deps) – press F5 if it stalls</div>
<div id="wrap"><img id="f" src="/frame.png?ts=0"></div>
<script>
const img = document.getElementById('f');
let t=0;
function tick(){
  t++;
  img.src = '/frame.png?ts=' + t;
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);
</script>
</body></html>
"""

class _Handler(BaseHTTPRequestHandler):
    latest_png: bytes = b""
    width: int = 960
    height: int = 600

    def do_GET(self):
        if self.path.startswith("/frame.png"):
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.end_headers()
            self.wfile.write(self.latest_png or b"")
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(_HTML)

    def log_message(self, fmt, *args):
        # silence
        return

class _ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

def _encode_png(pixels, w, h) -> bytes:
    import struct, zlib
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag+data) & 0xffffffff)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    raw = bytearray()
    stride = w*4
    for y in range(h):
        raw.append(0)
        start = y*stride
        raw.extend(pixels[start:start+stride])
    compressed = zlib.compress(bytes(raw), level=6)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")

def run(ui_callable, fps=60, size=(960,600), port=8765, open_browser=True):
    w, h = size
    handler = _Handler
    handler.width = w
    handler.height = h
    server = _ThreadingHTTPServer(("127.0.0.1", port), handler)

    def render_loop():
        import time
        from lygui.core import NewFrame, Render
        from lygui.renderers.software import create_framebuffer, fill_rect, draw_label
        from lygui.utils.color import rgba
        interval = 1.0 / max(1, fps)
        while True:
            t0 = time.time()
            NewFrame()
            ui_callable()
            cmds = Render()
            fb = create_framebuffer(w, h, rgba(220,221,225,255))
            # basic interpreter identical to other outputs
            for cmd, args, kwargs in cmds:
                if cmd == "BeginWindow":
                    name, (x,y), (ww,hh), flags = args
                    fill_rect(fb, w, x, y, ww, hh, rgba(246,246,248,255))
                    draw_label(fb, w, x+8, y+6, name, rgba(32,32,32,255))
                elif cmd == "Text":
                    txt, (xx,yy) = args
                    draw_label(fb, w, xx, yy, txt, rgba(24,24,24,255))
                elif cmd == "Button":
                    label, (xx,yy), (bw,bh), wid = args
                    fill_rect(fb, w, xx, yy, bw, bh, rgba(236,236,236,255))
                    draw_label(fb, w, xx+6, yy+8, label, rgba(10,10,10,255))
                elif cmd == "Checkbox":
                    label, (xx,yy), value, wid = args
                    fill_rect(fb, w, xx, yy, 18, 18, rgba(255,255,255,255))
                    if value: fill_rect(fb, w, xx+3, yy+9, 2, 2, rgba(30,136,229,255))
                    draw_label(fb, w, xx+24, yy+1, label, rgba(10,10,10,255))
                elif cmd == "InputText":
                    label, (xx,yy), width, value, wid = args
                    draw_label(fb, w, xx, yy-16, label, rgba(10,10,10,255))
                    fill_rect(fb, w, xx, yy, width, 22, rgba(255,255,255,255))
                    draw_label(fb, w, xx+6, yy+3, str(value), rgba(10,10,10,255))
                elif cmd == "SliderFloat":
                    label, (xx,yy), width, v, vmin, vmax, wid = args
                    draw_label(fb, w, xx, yy-16, f"{label}: {v:.3f}", rgba(10,10,10,255))
                    fill_rect(fb, w, xx, yy+8, width, 6, rgba(230,230,230,255))
                    t = 0.0 if vmax==vmin else (v - vmin) / (vmax - vmin)
                    kx = int(xx + t * width)
                    fill_rect(fb, w, kx-3, yy+4, 6, 14, rgba(120,120,120,255))
            png = _encode_png(fb, w, h)
            handler.latest_png = png
            t1 = time.time()
            dt = t1 - t0
            remaining = interval - dt
            if remaining > 0:
                time.sleep(remaining)

    t = threading.Thread(target=render_loop, daemon=True)
    t.start()

    url = f"http://127.0.0.1:{port}/"
    if open_browser:
        webbrowser.open(url, new=1, autoraise=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()