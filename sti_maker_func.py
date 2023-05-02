# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

def real_resolution(context):
    # count real resolution of the final render
    res_x = context.scene.render.resolution_x
    res_y = context.scene.render.resolution_y
    if context.scene.render.resolution_percentage != 100:
        res_x = int(res_x * (context.scene.render.resolution_percentage / 100))
        res_y = int(res_y * (context.scene.render.resolution_percentage / 100))
    return res_x, res_y
