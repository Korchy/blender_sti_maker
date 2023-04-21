# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

from bpy.types import Operator
from bpy.utils import register_class, unregister_class
from .sti_maker import STIMaker


class STI_MAKER_OT_main(Operator):
    bl_idname = 'sti_maker.main'
    bl_label = 'sti_maker: main'
    bl_description = 'sti_maker - main operator'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        STIMaker.save_to_sti(
           context=context
        )
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return True


def register():
    register_class(STI_MAKER_OT_main)


def unregister():
    unregister_class(STI_MAKER_OT_main)
