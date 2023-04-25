# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

import subprocess
import sys
import os
from PIL import Image
import bpy
import numpy as np
from .sti_maker_sti import STI16BRGB565, STI8BI, STI8BIA

from ctypes import c_uint8, c_uint32

class STIMaker:

    _mode = 'IMAGE'     # IMAGE, ANIMATION
    _render_recall_interval = 0.25  # sek
    _data = []      # block for summary rendered data [[frame 1 data in rgba], [], ...]
    _frames = []    # list of dicts, each dict - each frame info [{"width": 1, ...}, ...]

    @classmethod
    def viewer_node_to_sti(cls, context):
        # save Viewer Node data to .sti
        # pixels from Viewer Node (RGBA)
        cls._data = [context.blend_data.images['Viewer Node'].pixels,]
        cls._frames = [
            {
                'width': context.scene.render.resolution_x,
                'height': context.scene.render.resolution_y,
                'data_length': int(len(cls._data[0]) / 4)  # rgba -> index to palette
            }
        ]
        # cls._data = [context.blend_data.images['red.png'].pixels,]
        # pixels_rgba = context.blend_data.images['su.png'].pixels
        if cls._data:
            pixels_rgba = cls._data
            # clamp to 0-1 range
            #   pixels from Viewer Node comes in dynamic color space, value could be grater 1
            #   need to clamp range to each color value to 0-1
            #   now solved with the Convert Colorspace node in compositor (from sRGB to FilmicsRGB)

            # convert to the required STI mode
            if context.scene.sti_maker_props.format == 'STIRGB565':
                # always 1 frame
                pixels_rgba = pixels_rgba[0]
                # convert data array from RGBA to RGB565
                pixels_rgb565 = cls._pixels_rgba_rgb565(pixels_rgba=pixels_rgba)
                # create .sti
                sti = STI16BRGB565(
                    pixels_rgb565=pixels_rgb565,
                    width=context.scene.render.resolution_x,
                    height=context.scene.render.resolution_y
                )
                # save to file
                sti.save_image(path='d:/', file_name='1')
            elif context.scene.sti_maker_props.format == 'STI8I':
                # join all frames to single image
                pixels_rgba = np.concatenate(np.array(pixels_rgba))
                # convert to RGB256 and get indices (body) and palette
                indices, palette = cls._pixels_rgba_rgb256(pixels_rgba=pixels_rgba)
                # create .sti
                # print('paleter', palette, len(palette))
                sti = STI8BI(
                    indices=indices,
                    palette=palette,
                    frames=cls._frames
                )
                # save to file
                sti.save_image(path='d:/', file_name='2')
            elif context.scene.sti_maker_props.format == 'STI8IA':
                pass
            print('STI saved')

    @classmethod
    def render_to_sti(cls, context):
        # render to .sti
        cls._mode = 'IMAGE'
        cls._add_handlers()
        # start render
        if not bpy.app.timers.is_registered(cls._render):
            bpy.app.timers.register(
                cls._render,
                first_interval=cls._render_recall_interval
            )

    @classmethod
    def _pixels_rgba_rgb256(cls, pixels_rgba: [list, tuple]):
        """
        Convert pixels data array from image in range 0-1 (float) [r, g, b, a, ...]
        to data in 256 indexed format - palette + body with indices to palette
        each index in body refers to color in palette

        :param pixels_rgba: pixels data array [0-1, ...]
        :return: indices array [0-256, ...], palette [r, g, b, ...]
        """
        # data to numpy.array to increase processing speed
        pixels_0_1 = np.asarray(pixels_rgba)    # [r (0-1), g (0-1), b (0-1), a(0-1), ...]
        # print(len(pixels_0_1))
        # print(pixels_0_1[:10])
        # convert from 0-1 to 0-255 in linear color space
        pixels_0_255 = np.array(list(map(cls._from_linear, pixels_0_1)))  # [r (0-255), ...]
        pixels_0_255 = np.array(list(map(lambda c: c.astype(np.uint8), pixels_0_255)))  # [r (0-255), ...]
        # print('p_0_255', len(pixels_0_255))
        # print(pixels_0_255[:10])
        # split to chunks by 4 elements - 1 color
        pixels_rgba = np.array_split(pixels_0_255, int(len(pixels_0_255) / 4))   # [[r (0-355), g, b, a], ...]
        pixels_rgba = np.array(pixels_rgba)
        # print('p_0_255_splited', pixels_rgba[:10])

        p = np.array(np.array_split(pixels_rgba, bpy.context.scene.render.resolution_x))
        # print('p', len(p))
        # print(p[:2])

        data = Image.fromarray(p)   # - Pillow Image in RGBA format
        # convert to RGB 256 colors
        im = data.convert('P', palette=Image.ADAPTIVE, colors=256)
        # palette
        palette = im.getpalette()
        # print(palette, len(palette))

        indices = [p for p in im.getdata()]
        # print('indiecs', indices, max(indices))

        # p = np.array(list(map(lambda c: (c[0] << 24) | (c[1] << 16) | c[2] << 8 | c[3], pixels_rgba)))
        # p = np.array(list(map(cls._rgba_rgb888, pixels_rgba)))
        # print('p', len(p))
        # print(p[:10])
        # p = p.astype(np.uint32)
        # p = np.reshape(p, (512, 512))
        # print(len(p))
        # print(p[:10])
        # r = [tuple(c) for c in pixels_rgba]
        # print(r[:10])

        # pixels_rgba = np.array(map(tuple, pixels_rgba))  # [r (0-255), ...]
        # print(pixels_rgba[:10])
        # # pixels_rgba = np.array(pixels_rgba)
        # arr = np.reshape(pixels_rgba, (512, 512))
        # print(arr)
        # arr = np.array(arr)
        # print(type(arr))


        data.save('d:/00.png')


        # # image data should be flipped by Y and by X to get right order
        # #   now solved with the "Flip" node in Compositor
        # return indices, palette
        return indices, palette

    @classmethod
    def _pixels_rgba_rgb565(cls, pixels_rgba: [list, tuple]):
        """
        Convert pixels data array from image in range 0-1 (float) [r, g, b, a, ...]
        to pixels data array in RGB565 format (single 2-bytes integer) [rgb565, rgb565,...]

        :param pixels_rgba: pixels data array [0-1, ...]
        :return: pixels data array [0-65535, ...]
        """
        # data to numpy.array to increase processing speed
        pixels_0_1 = np.asarray(pixels_rgba)    # [r (0-1), g (0-1), b (0-1), a(0-1), ...]
        # convert from 0-1 to 0-255 in linear color space
        pixels_0_255 = np.array(list(map(cls._from_linear, pixels_0_1)))  # [r (0-255), ...]
        # split to chunks by 4 elements - 1 color
        pixels_rgba = np.array_split(pixels_0_255, int(len(pixels_0_255) / 4))   # [[r (0-355), g, b, a], ...]
        # convert each RGBA chunk to RBG565 single value
        pixels_rgb565 = np.array(list(map(cls._rgba_rgb565, pixels_rgba)))  # [0-65536, ...]
        # image data should be flipped by Y and by X to get right order
        #   now solved with the "Flip" node in Compositor
        return pixels_rgb565

    @staticmethod
    # def _rgba_rgb565(r: int, g: int, b: int, a: int):
    def _rgba_rgb565(rgba: [list, tuple]) -> int:
        """
        Convert single pixel data from RGBA format to RGB565 format (0-65535)

        :param rgba: pixel data in RGBA format (0-255, 0-255, 0-255, 0-255)
        :return: pixel data in RGB565 format (0-65535) - two bytes integer
        """
        r, g, b, a = rgba
        r = r >> 3
        g = g >> 2
        b = b >> 3
        rgb565 = 0x0000
        rgb565 |= ((r & 0x1F) << 11)
        rgb565 |= ((g & 0x3F) << 5)
        rgb565 |= (b & 0x1F)
        return rgb565

    @staticmethod
    # def _rgba_rgb565(r: int, g: int, b: int, a: int):
    def _rgba_rgb888(rgba: [list, tuple]) -> int:
        """
        Convert single pixel data from RGBA format to RGB565 format (0-65535)

        :param rgba: pixel data in RGBA format (0-255, 0-255, 0-255, 0-255)
        :return: pixel data in RGB565 format (0-65535) - two bytes integer
        """
        r, g, b, a = rgba
        r = r & 0xFF
        g = g & 0xFF
        b = b & 0xFF
        a = a & 0xFF
        rgb888 = (r << 24) + (g << 16) + (b << 8) + a
        # rgb888 = (a << 24) + (r << 16) + (g << 8) + b
        # rgb888 = c_uint32((c_uint8 * 4)(*rgba))
        return rgb888

    @staticmethod
    def _from_linear(color_value: float):
        """
        Convert color value from 0-1 range to 0-255 range
        From linear color space (0.5 = 188) to radl color space (0.5 = 127)

        :param color_value: color value in 0-1 range
        :return: color value in 0-255 range
        """
        if color_value <= 0.0031308:
            return int(12.92 * color_value * 255.99)
        else:
            return int((1.055 * color_value ** (1 / 2.4) - 0.055) * 255.99)

    @classmethod
    def _render(cls):
        # start render process
        if cls._mode == 'ANIMATION':
            rez = bpy.ops.render.render(
                'INVOKE_DEFAULT',
                animation=True,
                use_viewport=True
            )
        else:
            rez = bpy.ops.render.render(
                'INVOKE_DEFAULT',
                use_viewport=True
            )
        if rez == {'CANCELLED'}:
            # retry with timer
            return cls._render_recall_interval

    @classmethod
    def _add_handlers(cls):
        # init render handlers
        if cls._on_render_init not in bpy.app.handlers.render_init:
            bpy.app.handlers.render_init.append(cls._on_render_init)
        if cls._on_render_post not in bpy.app.handlers.render_post:
            bpy.app.handlers.render_post.append(cls._on_render_post)
        if cls._on_render_complete not in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.append(cls._on_render_complete)
        if cls._on_render_cancel not in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.append(cls._on_render_cancel)

    @classmethod
    def _remove_handlers(cls):
        # init render handlers
        if cls._on_render_init in bpy.app.handlers.render_init:
            bpy.app.handlers.render_init.remove(cls._on_render_init)
        if cls._on_render_post in bpy.app.handlers.render_post:
            bpy.app.handlers.render_post.remove(cls._on_render_post)
        if cls._on_render_complete in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.remove(cls._on_render_complete)
        if cls._on_render_cancel in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(cls._on_render_cancel)

    @classmethod
    def _on_render_init(cls, *args):
        # whole render starts
        context = bpy.context
        cls._data = []
        cls._frames = []
        print('on render init')

    @classmethod
    def _on_render_post(cls, *args):
        # render of the current frame is completed
        context = bpy.context
        node = cls._output_node(context=context)
        if node:
            # pixels from Viewer Node (RGBA)
            cls._data.append(node.pixels)
            # frame info
            cls._frames.append(
                {
                    'width': context.scene.render.resolution_x,
                    'height': context.scene.render.resolution_y,
                    'data_length': len(node.pixels) / 4     # rgba -> index to palette
                }
            )
        print('on render post')

    @classmethod
    def _on_render_complete(cls, *args):
        # the whole render is completed
        context = bpy.context
        print('on render complete')
        cls._remove_handlers()
        # write to .sti
        cls.viewer_node_to_sti(
            context=context
        )

    @classmethod
    def _on_render_cancel(cls, *args):
        # render cancelled by user
        print('on render cancel')
        cls._remove_handlers()

    @staticmethod
    def _output_node(context):
        # get data output Viewer Node from Compositing
        return next((node for node in context.scene.node_tree.nodes
                     if node.type == 'VIEWER' and node.label == 'STI OUTPUT'), None)

    @staticmethod
    def install_pillow():
        # install Pillow (PIL) package to Blender
        python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
        target = os.path.join(sys.prefix, 'lib', 'site-packages')
        # update pip
        subprocess.call([python_exe, '-m', 'ensurepip'])
        subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'])
        # install Pillow
        subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'pillow', '-t', target])
        print('Pillow installed')
