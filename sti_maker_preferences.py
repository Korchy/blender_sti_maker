# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

from bpy.types import AddonPreferences
from bpy.utils import register_class, unregister_class


class STI_MAKER_preferences(AddonPreferences):

    bl_idname = __package__

    def draw(self, context):
        # install Pillow (PIL) module operator
        layout = self.layout
        layout.label(
            text='You need to install Pillow package first to save to .sti format'
        )
        box = layout.box()
        box.label(
            text='Be sure you are running Blender with the Administrative (root) rights and press the button'
        )
        box.operator(
            operator='sti_maker.install_pillow',
            icon='PACKAGE'
        )


def register():
    register_class(STI_MAKER_preferences)


def unregister():
    unregister_class(STI_MAKER_preferences)
