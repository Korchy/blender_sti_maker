# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker
#
#   Source by Jagged Alliance 2 Stracciatella Team
#       https://github.com/ja2-stracciatella

import io
import struct


class ETRLE:

    IS_COMPRESSED_BYTE_MASK = 0x80
    NUMBER_OF_BYTES_MASK = 0x7F

    @classmethod
    def compress(cls, indices: [list, tuple], width: int, height: int):
        """
        Compress STI image date (indices) with ETRLE

        :param indices: image indices, 1-byte array of indices to the palette
        :param width: width in pix
        :param height: height in pix
        :return: compressed indices array
        """
        compressed_indices = io.BytesIO()
        for i in range(height):
            # compress by rows
            compressed_indices.write(
                cls._compress_row(
                    row=indices[i * width:(i + 1) * width]
                )
            )
            compressed_indices.write(b'\x00')
        return compressed_indices.getvalue()

    @classmethod
    def _compress_row(cls, row: [list, tuple]):
        """
        Compress single row of image indices
        :param row: row of indices
        :return: compressed row of indices
        """
        current = 0
        source_length = len(row)
        compressed_buffer = io.BytesIO()

        while current < source_length:
            runtime_length = 0
            if row[current] == 0:
                while current + runtime_length < source_length and row[current + runtime_length] == 0 \
                        and runtime_length < cls.NUMBER_OF_BYTES_MASK:
                    runtime_length += 1
                compressed_buffer.write(
                    struct.pack('<B', runtime_length | cls.IS_COMPRESSED_BYTE_MASK)
                )
            else:
                while current + runtime_length < source_length \
                        and row[current + runtime_length] != 0 \
                        and runtime_length < cls.NUMBER_OF_BYTES_MASK:
                    runtime_length += 1
                compressed_buffer.write(
                    struct.pack('<B', runtime_length)
                )
                compressed_buffer.write(
                    struct.pack('<{}B'.format(runtime_length), * row[current:current+runtime_length])
                )
            current += runtime_length
        return compressed_buffer.getvalue()
