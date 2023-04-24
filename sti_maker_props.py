# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

from bpy.props import EnumProperty, PointerProperty
from bpy.types import PropertyGroup, Scene
from bpy.utils import register_class, unregister_class


class STI_MAKER_Props(PropertyGroup):

    format: EnumProperty(
        name='Format',
        items=[
            ('STIRGB565', 'STI RGB 565', 'STI RGB 565', 1),
            ('STI8I', 'STI 8 bit Indexed', 'STI 8 bit Indexed', 2),
            ('STI8IA', 'STI 8 bit Indexed Animated', 'STI 8 bit Indexed Animated', 3)
        ],
        default='STIRGB565'
    )


def register():
    register_class(STI_MAKER_Props)
    Scene.sti_maker_props = PointerProperty(type=STI_MAKER_Props)


def unregister():
    del Scene.sti_maker_props
    unregister_class(STI_MAKER_Props)
