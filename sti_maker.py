# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

import subprocess
import sys
import os
import bpy
from .sti_maker_sti import STI


class STIMaker:

    _mode = 'IMAGE'     # IMAGE, ANIMATION
    _render_recall_interval = 0.25  # sek

    @classmethod
    def render_to_sti(cls, context, mode='IMAGE'):
        # render to .sti
        sti = STI(mode='8BIT_INDEXED')
        sti.save_image(path='d:/', file_name='1')


        # cls._mode = mode
        # cls._add_handlers()
        # # start render
        # if not bpy.app.timers.is_registered(cls._render):
        #     bpy.app.timers.register(
        #         cls._render,
        #         first_interval=cls._render_recall_interval
        #     )

    @classmethod
    def _render(cls):
        # start render process
        if cls._mode == 'ANIMATION':
            rez = bpy.ops.render.render(
                'INVOKE_DEFAULT',
                animation=True,
                use_viewport=True
            )
        else:
            rez = bpy.ops.render.render(
                'INVOKE_DEFAULT',
                use_viewport=True
            )
        if rez == {'CANCELLED'}:
            # retry with timer
            return cls._render_recall_interval

    @classmethod
    def _add_handlers(cls):
        # init render handlers
        if cls._on_render_init not in bpy.app.handlers.render_init:
            bpy.app.handlers.render_init.append(cls._on_render_init)
        if cls._on_render_post not in bpy.app.handlers.render_post:
            bpy.app.handlers.render_post.append(cls._on_render_post)
        if cls._on_render_complete not in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.append(cls._on_render_complete)
        if cls._on_render_cancel not in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.append(cls._on_render_cancel)

    @classmethod
    def _remove_handlers(cls):
        # init render handlers
        if cls._on_render_init in bpy.app.handlers.render_init:
            bpy.app.handlers.render_init.remove(cls._on_render_init)
        if cls._on_render_post in bpy.app.handlers.render_post:
            bpy.app.handlers.render_post.remove(cls._on_render_post)
        if cls._on_render_complete in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.remove(cls._on_render_complete)
        if cls._on_render_cancel in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(cls._on_render_cancel)

    @classmethod
    def _on_render_init(cls, *args):
        # whole render starts
        context = bpy.context
        print('on render init')

    @classmethod
    def _on_render_post(cls, *args):
        # render of the current frame is completed
        context = bpy.context
        print('on render post')

    @classmethod
    def _on_render_complete(cls, *args):
        # the whole render is completed
        context = bpy.context
        print('on render complete')
        cls._remove_handlers()
        # write to .sti
        sti = STI()
        sti.save_image(path='d:/1.sti')

    @classmethod
    def _on_render_cancel(cls, *args):
        # render cancelled by user
        print('on render cancel')
        cls._remove_handlers()

    @staticmethod
    def install_pillow():
        # install Pillow (PIL) package to Blender
        python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
        target = os.path.join(sys.prefix, 'lib', 'site-packages')
        # update pip
        subprocess.call([python_exe, '-m', 'ensurepip'])
        subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'])
        # install Pillow
        subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'pillow', '-t', target])
        print('Pillow installed')
