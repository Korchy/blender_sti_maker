# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

from ctypes import c_char, c_int16, c_ubyte, c_uint8, c_uint16, c_uint32, Structure


class STIHeader8bI(Structure):
    """
        8 bit indexed colors static or animated.
    """

    _fields_ = (
        ('cID', c_char * 4),                # ID
        ('uiOriginalSize', c_uint32),       # uncompressed image size in bytes
        ('uiStoredSize', c_uint32),         # compressed image size in bytes
        ('uiTransparentValue', c_uint32),   # index pf transparent color in palette
        ('fFlags', c_uint32),               # flag (sti format)
        ('usHeight', c_uint16),             # image height in pix
        ('usWidth', c_uint16),              # image width in pix
        ('uiNumberOfColours', c_uint32),    # number of colors in palette
        ('usNumberOfSubImages', c_uint16),  # number of frames in image
        ('ubRedDepth', c_uint8),            # red color depth
        ('ubGreenDepth', c_uint8),          # green color depth
        ('ubBlueDepth', c_uint8),           # blue color depth
        ('cIndexedUnused', c_ubyte * 11),   # unused - 11 bytes
        ('ubDepth', c_uint8),               # color depth
        ('cOffsetUnused', c_ubyte * 3),     # unused - 3 bytes
        ('uiAppDataSize', c_uint32),        # application data size in bytes
        ('cUnused', c_ubyte * 12),          # unused - 12 bytes
    )

    def __init__(self,byte_size: int,  animated: bool = False, frames: int = 1):
        super().__init__()

        self.cID = b'STCI'                      # always 'STCI'
        self.uiOriginalSize = byte_size
        self.uiStoredSize = byte_size
        self.uiTransparentValue = 0             # always 0
        self.fFlags = 41 if animated else 40    # always 40 (static) or 41 (animated)
        self.usHeight = 0                       # always 0
        self.usWidth = 0                        # always 0
        self.uiNumberOfColours = 256            # always 256
        self.usNumberOfSubImages = frames
        self.ubRedDepth = 8                     # always 8
        self.ubGreenDepth = 8                   # always 8
        self.ubBlueDepth = 8                    # always 8
        self.cIndexedUnused = (c_ubyte * 11)(*list(bytearray(0 * 11)))  # always 0
        self.ubDepth = 8                        # always 8
        self.cOffsetUnused = (c_ubyte * 3)(*list(bytearray(0 * 3)))     # always 0
        self.uiAppDataSize = (frames * 16 if animated else 0)
        self.cUnused = (c_ubyte * 12)(*list(bytearray(0 * 12)))         # always 0


class STI8bIPalette(Structure):
    """
        8 bit indexed image palette
    """

    _fields_ = (
        ('palette', c_uint8 * (3 * 256)),      # (r, g, b) * 256 = 768 bytes
    )

    def __init__(self, data: [list, tuple]):
        super().__init__()

        self.palette = (c_uint8 * (3 * 256))(*data)   # r, g, b, ...


class STI8bISubImage(Structure):
    """
        8 bit indexed image SubImage header
    """

    _fields_ = (
        ('uiDataOffset', c_uint32),         # offset of this frame data in image data block
        ('uiDataLength', c_uint32),         # frame size in bytes
        ('sOffsetX', c_int16),              # frame offset by X in pix
        ('sOffsetY', c_int16),              # frame offset by Y in pix
        ('usHeight', c_uint16),             # frame height in pix
        ('usWidth', c_uint16),              # frame width in pix
    )

    def __init__(self, width: int, height: int, frame_data_offset: int,
                 frame_size: int, frame_offset_x: int = 0, frame_offset_y: int = 0):
        super().__init__()

        self.uiDataOffset = frame_data_offset   # 0 for the first image, size of all prev images - for each next image
        self.uiDataLength = frame_size
        self.sOffsetX = frame_offset_x
        self.sOffsetY = frame_offset_y
        self.usHeight = height
        self.usWidth = width


class STIHeader16bRGB(Structure):
    """
        16 bit RGB565
    """

    _fields_ = (
        ('cID', c_char * 4),                # ID
        ('uiOriginalSize', c_uint32),       # uncompressed image size in bytes
        ('uiStoredSize', c_uint32),         # compressed image size in bytes
        ('uiTransparentValue', c_uint32),   # index pf transparent color in palette
        ('fFlags', c_uint32),               # flag (sti format)
        ('usHeight', c_uint16),             # image height in pix
        ('usWidth', c_uint16),              # image width in pix
        ('uiRedMask', c_uint32),            # red color mask
        ('uiGreenMask', c_uint32),          # greed color mask
        ('uiBlueMask', c_uint32),           # blue color mask
        ('uiAlphaMask', c_uint32),          # alpha mask
        ('ubRedDepth', c_uint8),            # red color depth
        ('ubGreenDepth', c_uint8),          # green color depth
        ('ubBlueDepth', c_uint8),           # blue color depth
        ('ubAlphaDepth', c_uint8),          # alpha depth
        ('ubDepth', c_uint8),               # color depth
        ('cOffsetUnused', c_ubyte * 3),     # unused - 3 bytes
        ('uiAppDataSize', c_uint32),        # application data size in bytes
        ('cUnused', c_ubyte * 12),          # unused - 12 bytes
    )

    def __init__(self, byte_size: int = 0, width: int = 0, height: int = 0):
        super().__init__()

        self.cID = b'STCI'              # always 'STCI'
        self.uiOriginalSize = byte_size
        self.uiStoredSize = byte_size
        self.uiTransparentValue = 0     # always 0
        self.fFlags = 4                 # always 4
        self.usHeight = height
        self.usWidth = width
        self.uiRedMask = 63488          # always 63488
        self.uiGreenMask = 2016         # always 2016
        self.uiBlueMask = 31            # always 31
        self.uiAlphaMask = 0            # always 0
        self.ubRedDepth = 5             # always 5
        self.ubGreenDepth = 6           # always 6
        self.ubBlueDepth = 5            # always 5
        self.ubAlphaDepth = 0           # always 0
        self.ubDepth = 16               # always 16
        self.cOffsetUnused = (c_ubyte * 3)(*list(bytearray(0 * 3)))     # always 0
        self.uiAppDataSize = 0          # always 0
        self.cUnused = (c_ubyte * 12)(*list(bytearray(0 * 12)))         # always 0


class STIHeader8bIBase(Structure):
    """
        8 bit indexed colors static or animated. Base structure (from sources)
    """

    _fields_ = (
        ('cID', c_char * 4),                # ID
        ('uiOriginalSize', c_uint32),       # uncompressed image size in bytes
        ('uiStoredSize', c_uint32),         # compressed image size in bytes
        ('uiTransparentValue', c_uint32),   # index pf transparent color in palette
        ('fFlags', c_uint32),               # flag (sti format)
        ('usHeight', c_uint16),             # image height in pix
        ('usWidth', c_uint16),              # image width in pix
        ('uiNumberOfColours', c_uint32),    # number of colors in palette
        ('usNumberOfSubImages', c_uint16),  # number of frames in image
        ('ubRedDepth', c_uint8),            # red color depth
        ('ubGreenDepth', c_uint8),          # green color depth
        ('ubBlueDepth', c_uint8),           # blue color depth
        ('cIndexedUnused', c_ubyte * 11),   # unused - 11 bytes
        ('ubDepth', c_uint8),               # color depth
        ('uiAppDataSize', c_uint32),        # application data size in bytes
        ('cUnused', c_ubyte * 15),          # unused - 15 bytes
    )

    def __init__(self, animated: bool = False, frames: int = 0, byte_size: int = 0,
                 width: int = 0, height: int = 0):
        super().__init__()

        self.cID = b'STCI'                      # always 'STCI'
        self.uiOriginalSize = byte_size
        self.uiStoredSize = byte_size
        self.uiTransparentValue = 0             # always 0
        self.fFlags = 41 if animated else 40    # always 40 (static) or 41 (animated)
        self.usHeight = height
        self.usWidth = width
        self.uiNumberOfColours = 256            # always 256
        self.usNumberOfSubImages = frames
        self.ubRedDepth = 8                     # always 8
        self.ubGreenDepth = 8                   # always 8
        self.ubBlueDepth = 8                    # always 8
        self.cIndexedUnused = (c_ubyte * 11)(*list(bytearray(0 * 11)))  # always 0
        self.ubDepth = 8                        # always 8
        self.uiAppDataSize = (frames * 16 if animated else 0)
        self.cUnused = (c_ubyte * 15)(*list(bytearray(0 * 15))) # always 0


class STIHeader16bRGBBase(Structure):
    """
        16 bit RGB565. Base structure (from sources)
    """

    _fields_ = (
        ('cID', c_char * 4),                # ID
        ('uiOriginalSize', c_uint32),       # uncompressed image size in bytes
        ('uiStoredSize', c_uint32),         # compressed image size in bytes
        ('uiTransparentValue', c_uint32),   # index pf transparent color in palette
        ('fFlags', c_uint32),               # flag (sti format)
        ('usHeight', c_uint16),             # image height in pix
        ('usWidth', c_uint16),              # image width in pix
        ('uiRedMask', c_uint32),            # red color mask
        ('uiGreenMask', c_uint32),          # greed color mask
        ('uiBlueMask', c_uint32),           # blue color mask
        ('uiAlphaMask', c_uint32),          # alpha mask
        ('ubRedDepth', c_uint8),            # red color depth
        ('ubGreenDepth', c_uint8),          # green color depth
        ('ubBlueDepth', c_uint8),           # blue color depth
        ('ubAlphaDepth', c_uint8),          # alpha depth
        ('ubDepth', c_uint8),               # color depth
        ('uiAppDataSize', c_uint32),        # application data size in bytes
        ('cUnused', c_ubyte * 15),          # unused - 15 bytes
    )

    def __init__(self, byte_size: int = 0, width: int = 0, height: int = 0):
        super().__init__()

        self.cID = b'STCI'              # always 'STCI'
        self.uiOriginalSize = byte_size
        self.uiStoredSize = byte_size
        self.uiTransparentValue = 0     # always 0
        self.fFlags = 4                 # always 4
        self.usHeight = height
        self.usWidth = width
        self.uiRedMask = 63488          # always 63488
        self.uiGreenMask = 2016         # always 2016
        self.uiBlueMask = 31            # always 31
        self.uiAlphaMask = 0            # always 0
        self.ubRedDepth = 5             # always 5
        self.ubGreenDepth = 6           # always 6
        self.ubBlueDepth = 5            # always 5
        self.ubAlphaDepth = 0           # always 0
        self.ubDepth = 16               # always 16
        self.uiAppDataSize = 0          # always 0
        self.cUnused = (c_ubyte * 15)(*list(bytearray(0 * 15)))     # always 0
