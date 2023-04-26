# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

from bpy.types import Operator
from bpy.utils import register_class, unregister_class
from .sti_maker import STIMaker


class STI_MAKER_OT_render_to_sti_rgb565(Operator):
    bl_idname = 'sti_maker.render_to_sti_rgb565'
    bl_label = 'Render RGB565'
    bl_description = 'Render static image to STI RGB565'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        STIMaker.render_to_sti_rgb565(
            context=context
        )
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return True


class STI_MAKER_OT_render_to_sti_8b_set(Operator):
    bl_idname = 'sti_maker.render_to_sti_8b_set'
    bl_label = 'Render 8bit Set'
    bl_description = 'Render set of images in STI 8bit'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        STIMaker.render_to_sti_8b_set(
            context=context
        )
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return True


class STI_MAKER_OT_render_to_sti_8b_anim(Operator):
    bl_idname = 'sti_maker.render_to_sti_8b_anim'
    bl_label = 'Render 8bit Animation'
    bl_description = 'Render animated image in STI 8bit'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        STIMaker.render_to_sti_8b_animation(
            context=context
        )
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return True


class STI_MAKER_OT_install_pillow(Operator):
    bl_idname = 'sti_maker.install_pillow'
    bl_label = 'Install Pillow (PIL)'
    bl_description = 'Install Pillow (PIL) package to Blender'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        STIMaker.install_pillow()
        return {'FINISHED'}


def register():
    register_class(STI_MAKER_OT_install_pillow)
    register_class(STI_MAKER_OT_render_to_sti_rgb565)
    register_class(STI_MAKER_OT_render_to_sti_8b_set)
    register_class(STI_MAKER_OT_render_to_sti_8b_anim)


def unregister():
    unregister_class(STI_MAKER_OT_render_to_sti_8b_anim)
    unregister_class(STI_MAKER_OT_render_to_sti_8b_set)
    unregister_class(STI_MAKER_OT_render_to_sti_rgb565)
    unregister_class(STI_MAKER_OT_install_pillow)
