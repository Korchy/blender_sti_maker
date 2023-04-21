# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

import os
from .sti_maker_sti_header import STIHeader8bI, STIHeader16bRGB


class STI:

    _header = None

    def __init__(self, mode: str):
        # init
        if mode == '8BIT_INDEXED':
            self._header = STIHeader8bI()
        elif mode == '8BIT_INDEXED_ANIMATED':
            self._header = STIHeader8bI(animated=True)
        elif mode == '16BIT_RGB':
            self._header = STIHeader16bRGB()

    def save_image(self, path: str, file_name: str):
        # save image
        full_path = os.path.join(path, file_name + '.sti')
        with open(full_path, 'wb') as file:
            file.write(self._header)
