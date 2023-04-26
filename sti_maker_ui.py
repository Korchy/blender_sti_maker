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
        layout = self.layout
        box = layout.box()
        box.label(text='RGB565')
        box.operator(
            operator='sti_maker.render_to_sti_rgb565',
            icon='RESTRICT_RENDER_OFF'
        )
        box = layout.box()
        box.label(text='8 bit Set')
        box.operator(
            operator='sti_maker.render_to_sti_8b_set',
            icon='PACKAGE'
        )
        # layout.prop(
        #     data=context.scene.sti_maker_props,
        #     property='format',
        #     expand=True
        # )
        box = layout.box()
        box.label(text='TEST')
        box.operator(
            operator='sti_maker.viewer_node_to_sti',
            icon='RESTRICT_RENDER_ON'
        )


def register():
    register_class(STI_MAKER_PT_panel)


def unregister():
    unregister_class(STI_MAKER_PT_panel)
