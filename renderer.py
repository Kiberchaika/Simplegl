from pathlib import Path
from pyrr import Matrix44, Vector3, Quaternion
import imgui
import moderngl
import moderngl_window as mglw
from moderngl_window.scene.camera import OrbitCamera
from moderngl_window import geometry
from moderngl_window.integrations.imgui import ModernglWindowRenderer
from PIL import Image
import numpy as np
import time
import os
from freetype import Face, FT_LOAD_RENDER, FT_LOAD_FORCE_AUTOHINT

class BaseWindow(mglw.WindowConfig):
    gl_version = (4, 3)
    resource_dir = (Path(__file__).parent).resolve()
    aspect_ratio = None
    vsync = False
    samples = 0
    clear_color = (0.0, 0.0, 1.0, 0.0)
    framerate = 120

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        imgui.create_context()
        self.wnd.ctx.error
        self.wnd.mouse_exclusivity = False

        self.imgui = ModernglWindowRenderer(self.wnd)

        current_folder = os.path.dirname(os.path.abspath(__file__))

        self.m_proj_default = Matrix44.identity(dtype='f4')
        self.m_model = Matrix44.identity(dtype='f4')

        self.quad = geometry.quad_2d()
        self.sphere = geometry.sphere()

        self.mouse_x = 0
        self.mouse_y = 0

        self.program_base = self.load_program(os.path.join(current_folder, 'shaders/base.glsl'))
        self.program_base['m_view'].write(Matrix44.from_translation((0.0, 0.0, 0.0), dtype='f4'))

        self.program_text = self.load_program(os.path.join(current_folder, 'shaders/text.glsl'))
        self.program_text['m_view'].write(Matrix44.from_translation((0.0, 0.0, 0.0), dtype='f4'))

        self.program_color = self.load_program(os.path.join(current_folder, 'shaders/color.glsl'))
        self.program_color['m_view'].write(Matrix44.from_translation((0.0, 0.0, 0.0), dtype='f4'))

        self.program_line = self.load_program(os.path.join(current_folder, 'shaders/line.glsl'))
        self.program_line['m_view'].write(Matrix44.from_translation((0.0, 0.0, 0.0), dtype='f4'))
        self.program_line['m_model'].write(Matrix44.from_translation((0.0, 0.0, 0.0), dtype='f4'))
        self.vbo_line = self.ctx.buffer(np.array([
            -0.5, -0.5, 0.0,
            0.5, -0.5, 0.0,
        ], dtype='f4'))
        self.vao_line = self.ctx.vertex_array(
            self.program_line,
            [(self.vbo_line, '3f', 'in_position')]
        )

        self.program_circle = self.load_program(os.path.join(current_folder, 'shaders/circle.glsl'))
        self.program_circle['m_view'].write(Matrix44.from_translation((0.0, 0.0, 0.0), dtype='f4'))
        self.program_circle['m_model'].write(Matrix44.from_translation((0.0, 0.0, 0.0), dtype='f4'))
        self.vbo_circle = self.ctx.buffer(np.array([
            -1.0, -1.0, 0.0,
        ], dtype='f4'))
        self.vao_circle = self.ctx.vertex_array(
            self.program_circle,
            [(self.vbo_circle, '3f', 'in_position')]
        )

        self.text_renderer = TextRenderer(self, os.path.join(current_folder, 'fonts/UbuntuMono-R.ttf') , 12)

    def draw_image(self, tex, x, y, w, h):
        tex.use(0)
        self.draw_rect((1.0, 1.0, 1.0, 1.0), x, y, w, h, True)

    def draw_rect(self, col, x, y, w, h, use_tex = False):
        translation = Matrix44.from_translation((x + w/2, y + h/2, 0.0), dtype='f4')
        scale = Matrix44.from_scale((w, h, 1.0), dtype='f4')
        model = translation * scale  
        if use_tex:
            self.program_base['m_model'].write(self.m_model * model)
            self.program_base['color'].value = col
            self.quad.render(self.program_base)
        else:
            self.program_color['m_model'].write(self.m_model * model)
            self.program_color['color'].value = col
            self.quad.render(self.program_color)

    def draw_line(self, color, p1, p2, width):
        self.vbo_line.write(np.array([
            p1[0], p1[1], p1[2] if len(p1) > 2 else 0.0,
            p2[0], p2[1], p2[2] if len(p1) > 2 else 0.0,
        ], dtype='f4'))
        self.program_line['m_model'].write(self.m_model)
        self.program_line['width'].value = width
        self.program_line['color'].value = color
        self.vao_line.render(moderngl.LINE_STRIP)

    def draw_line2(self, color, p1, p2, w):
        delta_x = p2[0] - p1[0]
        delta_y = p2[1] - p1[1]
        angle = np.arctan2(delta_y, delta_x)
        distance = np.sqrt(delta_x**2 + delta_y**2)
        rotation = Matrix44.from_eulers((0, angle, 0), dtype='f4')

        translation = Matrix44.from_translation((p1[0] + delta_x/2,p1[1] + delta_y/2, 0.0), dtype='f4')
        scale = Matrix44.from_scale((w, distance, 1.0), dtype='f4')
        model = translation * rotation * scale  
      
        self.program_color['m_model'].write(self.m_model * model)
        self.program_color['color'].value = color
        self.quad.render(self.program_color)

    def draw_circle(self, color, p, radius):
        self.vbo_circle.write(np.array([
            p[0], p[1], p[2] if len(p) > 2 else 0.0,
        ], dtype='f4'))
        self.program_circle['m_model'].write(self.m_model)
        self.program_circle['radius'].value = radius
        self.program_circle['color'].value = color
        self.vao_circle.render(moderngl.POINTS)

    def set_viewport(self, idx = 0):
        self.wnd.fbo.viewport = (self.viewports[idx][0], self.wnd.size[1] - (self.viewports[idx][1] + self.viewports[idx][3]), self.viewports[idx][2], self.viewports[idx][3])

    def check_inside_viewport(self, idx = 0):
        return self.mouse_x > self.viewports[idx][0] and self.mouse_x < self.viewports[idx][0] + self.viewports[idx][2] and self.mouse_y > self.viewports[idx][1] and self.mouse_y < self.viewports[idx][1] + self.viewports[idx][3]

    def wait_for_next_frame(self, current_time: float):
        time.sleep(max(0, 1/self.framerate - (self.timer.time - current_time)))

    def key_event(self, key, action, modifiers):
        self.imgui.key_event(key, action, modifiers)
        keys = self.wnd.keys

        if action == keys.ACTION_PRESS:
            if key == keys.C:
                self.camera_enabled = not self.camera_enabled
                self.wnd.mouse_exclusivity = self.camera_enabled
                self.wnd.cursor = not self.camera_enabled
            if key == keys.SPACE:
                self.timer.toggle_pause()

    def set_default_camera_matrices(self):
        self.set_camera_matrices(Matrix44.identity(dtype='f4'), self.m_proj_default)

    def set_camera_matrices(self, m_view, m_proj):
        self.program_base['m_view'].write(m_view) 
        self.program_base['m_proj'].write(m_proj) 

        self.program_text['m_view'].write(m_view) 
        self.program_text['m_proj'].write(m_proj) 

        self.program_color['m_view'].write(m_view) 
        self.program_color['m_proj'].write(m_proj) 

        self.program_line['m_view'].write(m_view) 
        self.program_line['m_proj'].write(m_proj) 

        self.program_circle['m_view'].write(m_view) 
        self.program_circle['m_proj'].write(m_proj) 

    def resize(self, width: int, height: int):
        self.m_proj_default = Matrix44.from_scale((1.0, -1.0, 1.0), dtype='f4') * Matrix44.orthogonal_projection(
            0, width,
            0, height,
            -1.0, 1.0,
            dtype='f4',
        )
        self.imgui.resize(width, height)

    def mouse_position_event(self, x, y, dx, dy):
        self.imgui.mouse_position_event(x, y, dx, dy)

        self.mouse_x = x
        self.mouse_y = y  

    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)

    def mouse_scroll_event(self, x_offset, y_offset):
        self.imgui.mouse_scroll_event(x_offset, y_offset)

    def mouse_press_event(self, x, y, button):
        self.imgui.mouse_press_event(x, y, button)

    def mouse_release_event(self, x, y, button):
        self.imgui.mouse_release_event(x, y, button)

    def unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)
 

class TextRenderer:
    def __init__(self, mywindow, font_file: str, size: int):
        self.mywindow = mywindow
        self.font_file = font_file
        self.font_size = size

        self.setup_font()
        self.setup_buffers()

    def setup_font(self):
        # Load font and check it is monotype
        face = Face(self.font_file)
        face.set_char_size(self.font_size * 64)
        if not face.is_fixed_width:
            raise ValueError('Font is not monotype.')

        # Determine largest glyph size
        width, height, ascender, descender = 0, 0, 0, 0
        for c in range(32, 128):
            face.load_char(chr(c), FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT)
            bitmap = face.glyph.bitmap
            width = max(width, bitmap.width)
            ascender = max(ascender, face.glyph.bitmap_top)
            descender = max(descender, bitmap.rows - face.glyph.bitmap_top)
        height = ascender + descender

        self.char_width = width
        self.char_height = height

        # Generate texture data
        data = np.zeros((height * 6, width * 16), dtype='u1')
        for j in range(5, -1, -1):
            for i in range(16):
                face.load_char(chr(32 + j * 16 + i), FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT)
                bitmap = face.glyph.bitmap
                x = i * width + face.glyph.bitmap_left
                y = j * height + ascender - face.glyph.bitmap_top
                data[y:y + bitmap.rows, x:x + bitmap.width].flat = bitmap.buffer

        self.texture_height, self.texture_width = data.shape

        # Create texture
        self.texture = self.mywindow.ctx.texture((self.texture_width, self.texture_height), 1, data=data.tobytes())
        self.texture.build_mipmaps()

    def setup_buffers(self):
        self.vbo = self.mywindow.ctx.buffer(reserve=4096)
        self.ibo = self.mywindow.ctx.buffer(reserve=4096)

        self.vao = self.mywindow.ctx.vertex_array(
            self.mywindow.program_text,
            [
                (self.vbo, '2f 2f', 'in_position', 'in_texcoord_0'),
            ],
            index_buffer=self.ibo
        )


    def draw(self, color, p, text):
        vertices = []
        indices = []

        char_width = self.char_width
        char_height = self.char_height
        texture_width = self.texture_width
        texture_height = self.texture_height

        x_offset = 0
        y_offset = 0

        for char in text:
            if char == '\n':
                y_offset += char_height
                x_offset = 0
                continue

            char_index = ord(char) - 32
            tx = (char_index % 16) * char_width
            ty = (char_index // 16) * char_height   

            x0, y0 = x_offset, y_offset
            x1, y1 = x_offset + char_width, y_offset + char_height

            s0, t0 = tx / texture_width, ty / texture_height
            s1, t1 = (tx + char_width) / texture_width, (ty + char_height) / texture_height

            index_offset = len(vertices) // 4
            vertices.extend([
                x0, y0, s0, t0, 
                x1, y0, s1, t0,  
                x0, y1, s0, t1,  
                x1, y1, s1, t1,   
            ])
            indices.extend([
                index_offset, index_offset + 1, index_offset + 2,
                index_offset + 2, index_offset + 1, index_offset + 3,
            ])

            x_offset += char_width

        self.vbo.clear()
        self.vbo.write(np.array(vertices, dtype='f4'))
        
        self.ibo.clear()
        self.ibo.write(np.array(indices, dtype='u4'))

        translation = Matrix44.from_translation((p[0], p[1], p[2] if len(p) > 2 else 0.0), dtype='f4')

        self.mywindow.program_text['color'].value = color
        self.mywindow.program_text['m_model'].write(self.mywindow.m_model * translation) 
        self.texture.use(0)
        self.vao.render()

    def __del__(self):
        self.texture.release()
        self.vbo.release()
        self.ibo.release()
        self.vao.release()
