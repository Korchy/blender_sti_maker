# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

from ctypes import c_uint16
import os
from .sti_maker_sti_struct import STIHeader8bI, STIHeader16bRGB, STI8bIPalette,\
    STI8bISubImage, STI8bIAuxObjectData
from .sti_maker_etrle import ETRLE

class STI16BRGB565:

    _header = None  # main image header
    _body = None    # image body (RGB color bytes)

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

    _header = None                  # main image header
    _palette = None                 # palette - single palette to all frames
    _frame_headers = []             # header for each frame
    _frame_indices_compressed = []  # indices to palette (body) of each frame (should be etrle compressed)

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
        # palette
        self._palette = STI8bIPalette(
            data=palette
        )
        # frame headers
        self._frame_headers = []
        self._frame_indices_compressed = []
        compressed_bytes_size = 0
        frame_data_offset = 0
        for frame in frames:
            # frame indices (body) compressed
            frame_indices_compressed = ETRLE.compress(
                indices=frame['indices'],
                width=frame['width'],
                height=frame['height']
            )
            # frame header - write information about compressed indices and use it later
            self._frame_headers.append(
                STI8bISubImage(
                    width=frame['width'],
                    height=frame['height'],
                    frame_data_offset=frame_data_offset,
                    frame_size=len(frame_indices_compressed)
                )
            )
            # full size of compressed indices
            compressed_bytes_size += len(frame_indices_compressed)
            # add frame information
            self._frame_indices_compressed.append(frame_indices_compressed)
            # offset to next frame
            frame_data_offset += len(frame_indices_compressed)
        # main header - last, because it needs information about compressed indices (body)
        self._header = STIHeader8bI(
            byte_size=len(indices),
            compressed_byte_size=compressed_bytes_size,
            frames=len(frames)
        )

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

    _header = None                  # main image header
    _palette = None                 # palette - single palette to all frames
    _frame_headers = []             # header for each frame
    _frame_indices_compressed = []  # indices to palette (body) of each frame (should be etrle compressed)

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
        # palette
        self._palette = STI8bIPalette(
            data=palette
        )
        # frame headers
        self._frame_headers = []
        self._frame_aux_datas = []
        self._frame_indices_compressed = []
        compressed_bytes_size = 0
        frame_data_offset = 0
        for frame in frames:
            # frame indices (body) compressed
            frame_indices_compressed = ETRLE.compress(
                indices=frame['indices'],
                width=frame['width'],
                height=frame['height']
            )
            # frame header - write information about compressed indices and use it later
            self._frame_headers.append(
                STI8bISubImage(
                    width=frame['width'],
                    height=frame['height'],
                    frame_data_offset=frame_data_offset,
                    frame_size=len(frame_indices_compressed)
                )
            )
            # full size of compressed indices
            compressed_bytes_size += len(frame_indices_compressed)
            # add frame information
            self._frame_indices_compressed.append(frame_indices_compressed)
            # offset to next frame
            frame_data_offset += len(frame_indices_compressed)
            # frame aux data
            self._frame_aux_datas.append(
                STI8bIAuxObjectData(
                    frames_in_direction=frame['frames_in_new_direction']
                )
            )
        # main header - last, because it needs information about compressed indices (body)
        self._header = STIHeader8bI(
            byte_size=len(indices),
            compressed_byte_size=compressed_bytes_size,
            animated=True,
            frames=len(frames)
        )

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
            for frame_aux_data in self._frame_aux_datas:
                file.write(frame_aux_data)
