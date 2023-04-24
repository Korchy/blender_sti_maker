# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

import subprocess
import sys
import os
import bpy
import numpy as np
from .sti_maker_sti import STI16BRGB565


class STIMaker:

    _mode = 'IMAGE'     # IMAGE, ANIMATION
    _render_recall_interval = 0.25  # sek

    @classmethod
    def viewer_node_to_sti(cls, context):
        # save Viewer Node data to .sti
        node = cls._output_node(context=context)
        if node:
            # pixels from Viewer Node (RGBA)
            pixels_rgba = context.blend_data.images['Viewer Node'].pixels
            # pixels_rgba = context.blend_data.images['su.png'].pixels
            # clamp to 0-1 range
            #   pixels from Viewer Node comes in dynamic color space, value could be grater 1
            #   need to clamp range to each color value to 0-1
            #   now solved with the Convert Colorspace node in compositor (from sRGB to FilmicsRGB)

            # convert to the required STI mode
            if context.scene.sti_maker_props.format == 'STIRGB565':
                # convert data array from RGBA to RGB565
                pixels_rgb565 = cls._pixels_rgba_rgb565(pixels_rgba=pixels_rgba)
                # save to .sty
                sti = STI16BRGB565(
                    pixels_rgb565=pixels_rgb565,
                    width=context.scene.render.resolution_x,
                    height=context.scene.render.resolution_y
                )
                sti.save_image(path='d:/', file_name='1')
            elif context.scene.sti_maker_props.format == 'STI8I':
                pass
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
    def _from_linear(color_value: float):
        """
        Convert color value from 0-1 range to 0-255 range
        From linear color space (0.5 = 188) to radl color space (0.5 = 127)

        :param color_value: color value in 0-1 range
        :return: color value in 0-255 range
        """
        if color_value <= 0.0031308:
            return int(12.92 * color_value * 255)
        else:
            return int((1.055 * color_value ** (1 / 2.4) - 0.055) * 255)

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
        print('on render init')

    @classmethod
    def _on_render_post(cls, *args):
        # render of the current frame is completed
        context = bpy.context
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
