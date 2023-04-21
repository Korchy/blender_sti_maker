# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

from bpy.types import Panel
from bpy.utils import register_class, unregister_class


class STI_MAKER_PT_panel(Panel):
    bl_idname = 'STI_MAKER_PT_panel'
    bl_label = 'STI Maker'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'STI Maker'

    def draw(self, context):
        self.layout.operator(
            operator='sti_maker.render_to_sti',
            icon='RESTRICT_RENDER_OFF'
        )
        self.layout.operator(
            operator='sti_maker.render_to_sti_anim',
            icon='RENDER_ANIMATION'
        )


def register():
    register_class(STI_MAKER_PT_panel)


def unregister():
    unregister_class(STI_MAKER_PT_panel)
