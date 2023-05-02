# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

import subprocess
import sys
import os
import tempfile
import bpy
import numpy as np
from .sti_maker_sti import STI16BRGB565, STI8BI, STI8BIA
from .sti_maker_render_rgb565 import STIMakerRenderRGB565
from .sti_maker_render_8bit import STIMakerRender8bSet


class STIMaker:

    _mode = 'IMAGE'     # IMAGE, ANIMATION
    _render_recall_interval = 0.25  # sek
    _data = []      # block for summary rendered data [[frame 1 data in rgba], [], ...]
    _frames = []    # list of dicts, each dict - each frame info [{"width": 1, ...}, ...]

    @classmethod
    def render_to_sti_8b_animation(cls, context):
        # render to .sti 8bit animation
        # check output nodes
        cls._check_compositor_nodes(context=context)
        # render
        STIMakerRender8bSet.start(
            context=context,
            on_render_complete_callback=cls._save_to_sti_b8_animation,
            params = (context,),
            frames=context.scene.sti_maker_props.frames
        )

    @classmethod
    def _save_to_sti_b8_animation(cls, context, frames_data):
        # save to .sti 8bit w56 colors - animated image
        #     frames_data = {
        #         'width': context.scene.render.resolution_x,
        #         'height': context.scene.render.resolution_y,
        #         'pixels': pixels,
        #         'len_rgba': len(pixels),
        #         'len_bytes': int(len(pixels) / 4)
        #     }

        # join all frames to single image
        pixels = [frame['pixels'] for frame in frames_data]
        pixels_rgba = np.concatenate(np.array(pixels))
        # convert to RGB256 and get indices (body) and palette
        indices, palette = cls._pixels_rgba_rgb256(pixels_rgba=pixels_rgba)
        # split indices to separate frames from single image and add them to frames_data
        offset = 0
        for i, frame_data in enumerate(frames_data):
            frame_data['indices'] = indices[offset:offset + frame_data['len_bytes']]
            offset += frame_data['len_bytes']
        # create .sti in 8bit
        sti = STI8BIA(
            indices=indices,
            palette=palette,
            frames=frames_data
        )
        # save to file
        sti.save_image(path=cls.output_path(), file_name='8bitAnimation')

    @classmethod
    def render_to_sti_8b_set(cls, context):
        # render to .sti 8bit set
        # check output nodes
        cls._check_compositor_nodes(context=context)
        # render
        STIMakerRender8bSet.start(
            context=context,
            on_render_complete_callback=cls._save_to_sti_b8_set,
            params = (context,),
            frames=context.scene.sti_maker_props.frames
        )

    @classmethod
    def _save_to_sti_b8_set(cls, context, frames_data):
        # save to .sti 8bit w56 colors - set of images
        #     frames_data = {
        #         'width': context.scene.render.resolution_x,
        #         'height': context.scene.render.resolution_y,
        #         'pixels': pixels,
        #         'len_rgba': len(pixels),
        #         'len_bytes': int(len(pixels) / 4)
        #     }

        # join all frames to single image
        pixels = [frame['pixels'] for frame in frames_data]
        pixels_rgba = np.concatenate(np.array(pixels))
        # convert to RGB256 and get indices (body) and palette
        indices, palette = cls._pixels_rgba_rgb256(pixels_rgba=pixels_rgba)
        # split indices to separate frames from single image and add them to frames_data
        offset = 0
        for i, frame_data in enumerate(frames_data):
            frame_data['indices'] = indices[offset:offset + frame_data['len_bytes']]
            offset += frame_data['len_bytes']
        # create .sti in 8bit
        sti = STI8BI(
            indices=indices,
            palette=palette,
            frames=frames_data
        )
        # save to file
        sti.save_image(path=cls.output_path(), file_name='8bitSet')

    @classmethod
    def render_to_sti_rgb565(cls, context):
        # render to .sti RBG565
        # check output nodes
        cls._check_compositor_nodes(context=context)
        # render
        STIMakerRenderRGB565.start(
            context=context,
            on_complete_callback=cls._save_to_sti_rgb565,
            params = (context,)
        )

    @classmethod
    def _save_to_sti_rgb565(cls, context):
        # save to .sti RBG565
        # always 1 frame - get data from viewer node
        output_image = cls._output_image(context=context)
        if output_image:
            pixels_rgba = output_image.pixels
            # clamp to 0-1 range
            #   pixels from Viewer Node comes in dynamic color space, value could be grater 1
            #   need to clamp range to each color value to 0-1
            #   now solved with the Convert Colorspace node in compositor (from sRGB to FilmicsRGB)
            # convert data array from RGBA to RGB565
            pixels_rgb565 = cls._pixels_rgba_rgb565(pixels_rgba=pixels_rgba)
            # create .sti
            sti = STI16BRGB565(
                pixels_rgb565=pixels_rgb565,
                width=context.scene.render.resolution_x,
                height=context.scene.render.resolution_y
            )
            # save to file
            sti.save_image(path=cls.output_path(), file_name='RGB565')

    @classmethod
    def _pixels_rgba_rgb256(cls, pixels_rgba: [list, tuple]):
        """
        Convert pixels data array from image in range 0-1 (float) [r, g, b, a, ...]
        to data in 256 indexed format - palette + body with indices to palette
        each index in body refers to color in palette

        :param pixels_rgba: pixels data array [0-1, ...]
        :return: indices array [0-256, ...], palette [r, g, b, ...]
        """
        try:
            from PIL import Image
        except ImportError:
            print('Pillow module required to install!')
        # data to numpy.array to increase processing speed
        pixels_0_1 = np.asarray(pixels_rgba)    # [r (0-1), g (0-1), b (0-1), a(0-1), ...]
        # convert from 0-1 to 0-255 in linear color space
        pixels_0_255 = np.array(list(map(cls._from_linear, pixels_0_1)))  # [r (0-255), ...]
        # fetch to uint8 - to make it understandable for Pillow
        pixels_0_255 = np.array(list(map(lambda c: c.astype(np.uint8), pixels_0_255)))  # [r (0-255), ...]
        # split to chunks by 4 elements - 1 color
        pixels_rgba = np.array(np.array_split(pixels_0_255, int(len(pixels_0_255) / 4)))   # [[r (0-355), g, b, a], ...]
        # cover with one more array for Image.fromarray method
        pixels_for_pillow = np.array([pixels_rgba])
        # create Pillow Image in RGBA format
        pillow_image = Image.fromarray(pixels_for_pillow)
        # convert to RGB 256 colors
        pillow_image_255 = pillow_image.convert('P', palette=Image.ADAPTIVE, colors=256)
        # get palette
        palette = pillow_image_255.getpalette()
        # get body - indices to palette
        indices = [index for index in pillow_image_255.getdata()]
        # correct palette and indices - transparent color (0,0,0) must be the first in a palette
        if palette[:3] != [0, 0, 0]:
            # find transparent color (0,0,0) in palette
            transparent = None
            for i in range(0, len(palette), 3):
                if palette[i: i + 3] == [0, 0, 0]:
                    transparent = i
            # if exists
            if transparent is not None:
                transparent_idx = int(transparent / 3)
                # switch transparent with the first color
                palette[0:3], palette[transparent:transparent + 3] = palette[transparent:transparent + 3], palette[0:3]
                # switch all transparent indices with indices for the first color
                indices[:] = (0 if i == transparent_idx else (transparent_idx if i == 0 else i) for i in indices)
        # return indices (body) and palette
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
    def _rgba_rgb888(rgba: [list, tuple]) -> int:
        r, g, b, a = rgba
        r = r & 0xFF
        g = g & 0xFF
        b = b & 0xFF
        a = a & 0xFF
        rgb888 = (r << 24) + (g << 16) + (b << 8) + a
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

    @staticmethod
    def _output_node(context):
        # get data output Viewer Node from Compositing
        return next((node for node in context.scene.node_tree.nodes
                     if node.type == 'VIEWER' and node.label == 'STI OUTPUT'), None)

    @staticmethod
    def _check_compositor_nodes(context):
        # check compositing nodes exists
        context.scene.use_nodes = True
        node_tree = context.scene.node_tree
        output_viewer_node = next((node for node in node_tree.nodes if node.type == 'VIEWER'
                                   and node.label == 'STI OUTPUT'), None)
        if output_viewer_node is None:
            # create output composition nodes for STI
            # convert colorspace node for removing over-lights
            convert_colorspace_0 = node_tree.nodes.new('CompositorNodeConvertColorSpace')
            if hasattr(convert_colorspace_0, 'from_color_space'):
                convert_colorspace_0.from_color_space = 'sRGB'
            if hasattr(convert_colorspace_0, 'location'):
                convert_colorspace_0.location = (200, 265)
            if hasattr(convert_colorspace_0, 'to_color_space'):
                convert_colorspace_0.to_color_space = 'Filmic sRGB'
            # flip node to flip image by Y
            flip_0 = node_tree.nodes.new('CompositorNodeFlip')
            if hasattr(flip_0, 'axis'):
                flip_0.axis = 'Y'
            if hasattr(flip_0, 'location'):
                flip_0.location = (--20, 265)
            # output viewer node
            viewer_0 = node_tree.nodes.new('CompositorNodeViewer')
            if hasattr(viewer_0, 'label'):
                viewer_0.label = 'STI OUTPUT'
            if hasattr(viewer_0, 'location'):
                viewer_0.location = (480, 265)
            if hasattr(viewer_0, 'use_alpha'):
                viewer_0.use_alpha = True
            # links
            node_tree.links.new(convert_colorspace_0.outputs['Image'], viewer_0.inputs['Image'])
            node_tree.links.new(flip_0.outputs['Image'], convert_colorspace_0.inputs['Image'])
            output = next((node for node in node_tree.nodes if node.type == 'COMPOSITE'), None)
            if output:
                src_link = next((link for link in node_tree.links if link.to_node == output), None)
                if src_link:
                    node_tree.links.new(src_link.from_socket, flip_0.inputs['Image'])

    @staticmethod
    def _output_image(context):
        # get data output image (from Compositor Viewer Node)
        return next((image for image in context.blend_data.images
                     if image.name == 'Viewer Node'), None)

    @classmethod
    def output_path(cls) -> str:
        """ Return path to save STI

        :return: absolute path
        """
        path = None
        if bpy.context.scene.render.filepath:
            path = cls.abs_path(path=bpy.context.scene.render.filepath)
        if not path and bpy.data.filepath:
            path = os.path.dirname(os.path.abspath(bpy.data.filepath))
        if not path:
            path = tempfile.gettempdir()
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def abs_path(path):
        # returns absolute file path from path
        if path[:2] == '//':
            return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(bpy.data.filepath)), path[2:]))
        else:
            return os.path.abspath(path)

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
