from lygui import LyGui, NewFrame, Render

def test_frame_commands_nonempty():
    NewFrame()
    LyGui.Begin("T")
    LyGui.Text("X")
    LyGui.End()
    cmds = Render()
    assert any(c[0]=="BeginWindow" for c in cmds)
    assert any(c[0]=="Text" for c in cmds)