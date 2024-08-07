from pyrr import Matrix44
import imgui
import moderngl
import math
import moderngl_window as mglw
from renderer import BaseWindow

class WindowExample(BaseWindow):
    title = "Example 2d"
    window_size = (1300, 768)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def render(self, current_time, frametime):
        self.wnd.set_default_viewport()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.clear(0.5,0.5,0.5)

        self.set_default_camera_matrices()

        self.m_model = Matrix44.identity(dtype='f4')  
        self.draw_line((0.0, 1.0, 1.0, 1.0), (10, 10), (100, 10), 3)
        self.draw_circle((1.0, 0.0, 1.0, 1.0), (10, 50), 5)

        self.m_model = Matrix44.identity(dtype='f4')  
        self.m_model *= Matrix44.from_translation((200,10,0), dtype='f4')
        self.draw_rect((0.0,0.0,1.0,1.0), 0, 0, 100, 100)

        imgui.new_frame()

        imgui.set_next_window_size(300,self.wnd.size[1])
        imgui.set_next_window_position(self.wnd.size[0]-300,0)

        imgui.begin("Panel", False, imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE)
 
        if frametime:
            imgui.text(f"Frame time: {1000.0 * frametime:.1f} ms")
            imgui.text(f"Framerate: {math.ceil(1.0 / frametime)}")

        imgui.end()

        imgui.render()
        self.imgui.render(imgui.get_draw_data())

        self.wait_for_next_frame(current_time)

    def resize(self, width: int, height: int):
        super().resize(width, height)

    def mouse_drag_event(self, x, y, dx, dy):
        super().mouse_drag_event(x, y, dx, dy)

    def mouse_press_event(self, x, y, button):
        super().mouse_press_event(x, y, button)

    def mouse_release_event(self, x, y, button):
        super().mouse_release_event(x, y, button)

if __name__ == '__main__':
    mglw.run_window_config(WindowExample)