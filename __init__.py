# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

from . import sti_maker_ops
from . import sti_maker_ui
from . import sti_maker_preferences
from . import sti_maker_props


bl_info = {
    'name': 'STI Maker',
    'category': 'All',
    'author': 'Nikita Akimov',
    'version': (1, 0, 1),
    'blender': (3, 6, 0),
    'location': '',
    'doc_url': 'https://b3d.interplanety.org/en/',
    'tracker_url': 'https://b3d.interplanety.org/en/',
    'description': 'Render to STI (STCI)'
}


def register():
    sti_maker_props.register()
    sti_maker_preferences.register()
    sti_maker_ops.register()
    sti_maker_ui.register()


def unregister():
    sti_maker_ui.unregister()
    sti_maker_ops.unregister()
    sti_maker_preferences.unregister()
    sti_maker_props.unregister()


if __name__ == '__main__':
    register()
