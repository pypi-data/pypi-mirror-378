from lygui.renderers.software import create_framebuffer, fill_rect
from lygui.utils.color import rgba

def test_fill_rect_bounds():
    w,h = 64,64
    fb = create_framebuffer(w,h, rgba(0,0,0,255))
    fill_rect(fb, w, 10, 10, 10, 10, rgba(255,0,0,255))
    assert fb[(10*w+10)*4] == 255