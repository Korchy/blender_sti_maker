# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

import bpy
import functools


class STIMakerRenderRGB565:

    _render_call_interval = 0.25  # sek
    _on_render_complete_callback = None
    _params = None

    @classmethod
    def start(cls, context, on_complete_callback: callable, params: tuple):
        # add handlers
        cls._add_handlers()
        # callbacks
        cls._on_render_complete_callback = on_complete_callback
        # params    (context,)
        cls._params = params
        # start
        bpy.app.timers.register(
            functools.partial(cls._render),
            first_interval=0.5
        )

    @classmethod
    def _render(cls):
        # start render
        rez = bpy.ops.render.render('INVOKE_DEFAULT', use_viewport=True)
        if rez == {'CANCELLED'}:
            # retry with timer
            return cls._render_call_interval

    @classmethod
    def _on_render_complete(cls, *args):
        # render completed
        if cls._on_render_complete_callback:
            cls._on_render_complete_callback(*cls._params)
        cls._remove_handlers()
        cls._on_render_complete_callback = None
        cls._params = None

    @classmethod
    def _on_render_cancel(cls, *args):
        # render cancelled
        cls._remove_handlers()
        cls._on_render_complete_callback = None
        cls._params = None

    @classmethod
    def _add_handlers(cls):
        # init render handlers
        if cls._on_render_complete not in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.append(cls._on_render_complete)
        if cls._on_render_cancel not in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.append(cls._on_render_cancel)

    @classmethod
    def _remove_handlers(cls):
        # remove render handlers
        if cls._on_render_complete in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.remove(cls._on_render_complete)
        if cls._on_render_cancel in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(cls._on_render_cancel)
