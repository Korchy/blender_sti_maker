# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

from bpy.types import AddonPreferences
from bpy.props import StringProperty
from bpy.utils import register_class, unregister_class


class STI_MAKER_preferences(AddonPreferences):
    bl_idname = __package__

    pref1: StringProperty(
        name='pref1',
        default='sti_maker'
    )

    def draw(self, context):
        self.layout.prop(self, 'pref1')


def register():
    register_class(STI_MAKER_preferences)


def unregister():
    unregister_class(STI_MAKER_preferences)
