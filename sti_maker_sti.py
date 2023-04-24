# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

from ctypes import c_char, c_ubyte, c_uint, c_uint8, c_uint16, c_uint32, BigEndianStructure, Structure
import os
from .sti_maker_sti_header import STIHeader8bI, STIHeader16bRGB


class STI16BRGB565:

    _header = None
    _body = None

    def __init__(self, pixels_rgb565: [list, tuple], width: int, height: int):
        # init
        self._header = STIHeader16bRGB(
            # byte_size=int(len(pixels_rgb565) / 2),
            byte_size=len(pixels_rgb565)*2,
            width=width,
            height=height
        )
        self._body = (c_uint16 * len(pixels_rgb565))(*pixels_rgb565)
        # self._body = STIBody(_bytes=pixels_rgb565)

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

    def __init__(self, byte_size: int, width: int, height: int):
        # init
        self._header = STIHeader8bI(
            byte_size=byte_size,
            width=width,
            height=height
        )

    def save_image(self, path: str, file_name: str):
        # save image
        full_path = os.path.join(path, file_name + '.sti')
        with open(full_path, 'wb') as file:
            file.write(self._header)


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
