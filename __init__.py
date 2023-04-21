# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

from . import sti_maker_ops
from . import sti_maker_ui
from . import sti_maker_preferences
from .addon import Addon


bl_info = {
    'name': 'STI Maker',
    'category': 'All',
    'author': 'Nikita Akimov',
    'version': (1, 0, 0),
    'blender': (3, 6, 0),
    'location': '',
    'doc_url': 'https://b3d.interplanety.org/en/',
    'tracker_url': 'https://b3d.interplanety.org/en/',
    'description': 'Render to STI (STCI)'
}


def register():
    if not Addon.dev_mode():
        sti_maker_preferences.register()
        sti_maker_ops.register()
        sti_maker_ui.register()
    else:
        print('It seems you are trying to use the dev version of the '
              + bl_info['name']
              + ' add-on. It may work not properly. Please download and use the release version')


def unregister():
    if not Addon.dev_mode():
        sti_maker_ui.unregister()
        sti_maker_ops.unregister()
        sti_maker_preferences.unregister()


if __name__ == '__main__':
    register()
