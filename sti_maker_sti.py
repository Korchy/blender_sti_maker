# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

from ctypes import c_uint, c_uint8, c_uint16, c_uint32
import os
from .sti_maker_sti_header import STIHeader8bI, STIHeader16bRGB, STI8bIPalette,\
    STI8bISubImage
from .sti_maker_etrle import ETRLE

class STI16BRGB565:

    _header = None
    _body = None

    def __init__(self, pixels_rgb565: [list, tuple], width: int, height: int):
        """
        Create SIT image object
        :param pixels_rgb565: two-bytes color array [0-65536, ...]
        :param width: width in pix
        :param height: height in pix
        """
        self._header = STIHeader16bRGB(
            byte_size=len(pixels_rgb565)*2,
            width=width,
            height=height
        )
        self._body = (c_uint16 * len(pixels_rgb565))(*pixels_rgb565)    # 2-bytes values

    def save_image(self, path: str, file_name: str):
        # save image
        full_path = os.path.join(path, file_name + '.sti')
        with open(full_path, 'wb') as file:
            if self._header:
                file.write(self._header)
            if self._body:
                file.write(self._body)


class STI8BI:

    _header = None
    _palette = None
    _frame_headers = None
    _frame_indices_compressed = None
    # _body = None
    # _body_compressed = None

    def __init__(self, indices: [list, tuple], palette: [list, tuple],
                 frames: [list, tuple]):
        """
        Create SIT image object
        :param indices: pixels array
        :param frames: list of frames structures [[width, height, ], ...]
            frame {
                width = 0
                height = 0
            }
        """
        # main header
        self._header = STIHeader8bI(
            byte_size=len(indices),
            frames=len(frames)
        )
        # palette
        self._palette = STI8bIPalette(
            data=palette
        )
        # frame headers
        self._frame_headers = []
        self._frame_indices_compressed = []
        frame_data_offset = 0
        for i, frame in enumerate(frames):
            # frame header
            self._frame_headers.append(
                STI8bISubImage(
                    width=frame['width'],
                    height=frame['height'],
                    frame_data_offset=frame_data_offset,
                    frame_size=frame['data_length']
                )
            )
            # frame body
            self._frame_indices_compressed.append(
                ETRLE.compress(
                    indices=indices[frame_data_offset:frame['data_length']],
                    width=frame['width'],
                    height=frame['height']
                )
            )
            # offset to next frame
            frame_data_offset += frame['data_length']

    def save_image(self, path: str, file_name: str):
        # save image
        full_path = os.path.join(path, file_name + '.sti')
        with open(full_path, 'wb') as file:
            if self._header:
                file.write(self._header)
            if self._palette:
                file.write(self._palette)
            for frame_header in self._frame_headers:
                file.write(frame_header)
            for frame_indices in self._frame_indices_compressed:
                file.write(frame_indices)


class STI8BIA:

    _header = None

    def __init__(self, frames:int, byte_size: int, width: int, height: int):
        # init
        self._header = STIHeader8bI(
            animated=True,
            frames=frames,
            byte_size=byte_size,
            width=width,
            height=height
        )

    def save_image(self, path: str, file_name: str):
        # save image
        full_path = os.path.join(path, file_name + '.sti')
        with open(full_path, 'wb') as file:
            file.write(self._header)
