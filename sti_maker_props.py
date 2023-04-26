# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

from bpy.props import PointerProperty, StringProperty
from bpy.types import PropertyGroup, Scene
from bpy.utils import register_class, unregister_class


class STI_MAKER_Props(PropertyGroup):

    frames: StringProperty(
        name='Frames:',
        default=''
    )


def register():
    register_class(STI_MAKER_Props)
    Scene.sti_maker_props = PointerProperty(type=STI_MAKER_Props)


def unregister():
    del Scene.sti_maker_props
    unregister_class(STI_MAKER_Props)
