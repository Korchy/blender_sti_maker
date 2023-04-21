# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

from ctypes import c_char, c_uint16, c_uint32, Structure


class STIHeader8bI(Structure):
    """
        8 bit indexed colors static or animated
    """

    _fields_ = (
        ('cID', c_char * 4),                # ID
        ('uiOriginalSize', c_uint32),       # uncompressed image size in bytes
        ('uiStoredSize', c_uint32),         # compressed image size in bytes
        ('uiTransparentValue', c_uint32),   # index pf transparent color in palette
        ('fFlags', c_uint32),               # flag (sti format)
        ('usHeight', c_uint16),             # image height in pix
        ('usWidth', c_uint16),              # image width in pix
    )

    def __init__(self, animated: bool = False):
        self.cID = b'STCI'                      # always 'STCI'
        self.uiOriginalSize = 0
        self.uiStoredSize = 0
        self.uiTransparentValue = 0             # always 0
        self.fFlags = 41 if animated else 40    # always 40 (static) or 41 (animated)
        self.usHeight = 0
        self.usWidth = 0


class STIHeader16bRGB(Structure):
    """
        16 bit RGB
    """

    _fields_ = (
        ('cID', c_char * 4),                # ID
        ('uiOriginalSize', c_uint32),       # uncompressed image size in bytes
        ('uiStoredSize', c_uint32),         # compressed image size in bytes
        ('uiTransparentValue', c_uint32),   # index pf transparent color in palette
        ('fFlags', c_uint32),               # flag (sti format)
        ('usHeight', c_uint16),             # image height in pix
        ('usWidth', c_uint16),              # image width in pix
    )

    def __init__(self):
        self.cID = b'STCI'              # always 'STCI'
        self.uiOriginalSize = 0
        self.uiStoredSize = 0
        self.uiTransparentValue = 0     # always 0
        self.fFlags = 4                 # always 4
        self.usHeight = 0
        self.usWidth = 0
