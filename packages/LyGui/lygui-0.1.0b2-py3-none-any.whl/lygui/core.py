"""
LyGui core (beta) — zero-deps immediate-mode GUI.
No OS bindings. Software renderer consumes frame commands.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Tuple, Any, Optional, List

__all__ = ["LyGui", "GetIO", "GetStyle", "NewFrame", "Render"]

# --- Enums (subset) ---
class WindowFlags:
    NoTitleBar = 1 << 0
    NoResize = 1 << 1
    NoMove = 1 << 2
    NoScrollbar = 1 << 3

class Cond:
    Always = 0
    Once = 1
    FirstUseEver = 2
    Appearing = 3

# --- IO / Style ---
@dataclass
class IO:
    display_size: Tuple[int, int] = (800, 600)
    delta_time: float = 1/60.0
    mouse_pos: Tuple[int, int] = (0, 0)
    mouse_down: Tuple[bool, bool, bool] = (False, False, False)

@dataclass
class Style:
    WindowPadding: Tuple[int, int] = (10, 8)
    ItemSpacing: Tuple[int, int] = (8, 6)
    FramePadding: Tuple[int, int] = (6, 4)
    WindowRounding: int = 8
    FrameRounding: int = 4

@dataclass
class _WindowCtx:
    name: str
    pos: Tuple[int, int]
    size: Tuple[int, int]
    cursor: Tuple[int, int] = (0, 0)
    same_line: bool = False

@dataclass
class _Ctx:
    io: IO = field(default_factory=IO)
    style: Style = field(default_factory=Style)
    windows: Dict[str, _WindowCtx] = field(default_factory=dict)
    current: Optional[_WindowCtx] = None
    next_window_pos: Optional[Tuple[int, int]] = None
    next_window_size: Optional[Tuple[int, int]] = None
    frame_commands: List[Tuple[str, tuple, dict]] = field(default_factory=list)
    interactions: Dict[Any, Any] = field(default_factory=dict)

_ctx = _Ctx()

def GetIO() -> IO: return _ctx.io
def GetStyle() -> Style: return _ctx.style

def NewFrame():
    _ctx.frame_commands.clear()

def Render():
    return list(_ctx.frame_commands)

# backend hook
def _backend_set_interactions(interactions: Dict[Any, Any]):
    _ctx.interactions = interactions or {}

# layout
def _advance_cursor(w: int = 0, h: int = 24):
    win = _ctx.current
    if not win: return
    if win.same_line:
        cx, cy = win.cursor
        win.cursor = (cx + w + _ctx.style.ItemSpacing[0], cy)
        win.same_line = False
    else:
        win.cursor = (win.pos[0]+10, win.cursor[1] + h + _ctx.style.ItemSpacing[1])

def _alloc_rect(w: int, h: int) -> Tuple[int, int]:
    win = _ctx.current
    if not win: return (0, 0)
    x, y = win.cursor
    _advance_cursor(w=w, h=h)
    return (x, y)

class _LyGuiNS:
    def SetNextWindowPos(self, x: int, y: int, cond: int = Cond.Always):
        _ctx.next_window_pos = (x, y)
    def SetNextWindowSize(self, w: int, h: int, cond: int = Cond.Always):
        _ctx.next_window_size = (w, h)
    def Begin(self, name: str, flags: int = 0):
        pos = _ctx.next_window_pos or (50, 50)
        size = _ctx.next_window_size or (360, 220)
        _ctx.next_window_pos = None
        _ctx.next_window_size = None

        win = _ctx.windows.get(name)
        if not win:
            win = _WindowCtx(name=name, pos=pos, size=size, cursor=(pos[0]+10, pos[1]+32))
            _ctx.windows[name] = win
        else:
            win.pos, win.size = pos, size
            win.cursor = (pos[0]+10, pos[1]+32)
        _ctx.current = win
        _ctx.frame_commands.append(("BeginWindow", (name, win.pos, win.size, flags), {}))
        return True
    def End(self):
        if _ctx.current:
            _ctx.frame_commands.append(("EndWindow", (_ctx.current.name,), {}))
            _ctx.current = None
    def BeginChild(self, id: str, w: int = 0, h: int = 0, flags: int = 0):
        if not _ctx.current: return False
        _ctx.frame_commands.append(("BeginChild", (id, w, h, flags), {}))
        return True
    def EndChild(self):
        if not _ctx.current: return
        _ctx.frame_commands.append(("EndChild", (), {}))
    def SameLine(self):
        if not _ctx.current: return
        _ctx.current.same_line = True
    def Separator(self):
        if not _ctx.current: return
        _ctx.frame_commands.append(("Separator", (), {}))
        _advance_cursor(h=8)

    # widgets
    def Text(self, txt: str):
        if not _ctx.current: return
        x, y = _alloc_rect(200, 20)
        _ctx.frame_commands.append(("Text", (txt, (x, y)), {}))

    def Button(self, label: str, width: int = 100, height: int = 28):
        if not _ctx.current: return False
        x, y = _alloc_rect(width, height)
        wid = ("Button", label, (x, y), (width, height))
        _ctx.frame_commands.append(("Button", (label, (x, y), (width, height), wid), {}))
        return bool(_ctx.interactions.get(wid, False))

    def Checkbox(self, label: str, value: bool):
        if not _ctx.current: return (False, value)
        x, y = _alloc_rect(20, 20)
        wid = ("Checkbox", label, (x, y))
        new_val = _ctx.interactions.get(wid, value)
        changed = (new_val != value)
        _ctx.frame_commands.append(("Checkbox", (label, (x, y), new_val, wid), {}))
        return (changed, new_val)

    def InputText(self, label: str, value: str, width: int = 200):
        if not _ctx.current: return (False, value)
        x, y = _alloc_rect(width, 24)
        wid = ("InputText", label, (x, y), width)
        new_val = _ctx.interactions.get(wid, value)
        changed = (new_val != value)
        _ctx.frame_commands.append(("InputText", (label, (x, y), width, new_val, wid), {}))
        return (changed, new_val)

    def SliderFloat(self, label: str, v: float, v_min: float, v_max: float, width: int = 200):
        if not _ctx.current: return (False, v)
        x, y = _alloc_rect(width, 24)
        wid = ("SliderFloat", label, (x, y), width, v_min, v_max)
        new_val = float(_ctx.interactions.get(wid, v))
        new_val = max(min(new_val, v_max), v_min)
        changed = (abs(new_val - v) > 1e-12)
        _ctx.frame_commands.append(("SliderFloat", (label, (x, y), width, new_val, v_min, v_max, wid), {}))
        return (changed, new_val)

LyGui = _LyGuiNS()