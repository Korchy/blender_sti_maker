# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/blender_sti_maker

import bpy
import functools
import re
from .sti_maker_func import real_resolution


class STIMakerRender8bSet:
    mode = 'IDLE'  # current mode (IDLE, RENDER, CANCEL)
    _render_retry_interval = 0.5  # sek
    _render_call_interval = 0.25  # sek
    _frames = []  # scene frames to render
    _on_render_complete_callback = None
    _params = None
    _frames_data = []   # list of dicts, each dict - each frame info [{"width": 1, ...}, ...]

    @classmethod
    def start(cls, context, frames: [str, list], on_render_complete_callback: callable,
              params: tuple):
        # start render frame sequence
        cls.mode = 'IDLE'
        # convert scene frames to list
        cls._process_frames(
            context=context,
            frames=frames
        )
        # add handlers
        cls._add_handlers()
        # callbacks
        cls._on_render_complete_callback = on_render_complete_callback
        # params    (context,)
        cls._params = params
        # start
        bpy.app.timers.register(
            functools.partial(cls.next_frame, context),
            first_interval=0.5
        )

    @classmethod
    def _finish(cls, context):
        # finish - all frames are rendered
        if cls._on_render_complete_callback:
            cls._on_render_complete_callback(
                context=context,
                frames_data=cls._frames_data
            )
        # stop
        cls.stop(context=context)

    @classmethod
    def stop(cls, context):
        # stop render frame sequence
        # to 1 frame
        context.scene.frame_set(context.scene.frame_start)
        # clear
        cls._remove_handlers()
        cls._on_render_complete_callback = None
        cls._params = None
        cls._frames_data = []
        cls.mode = 'IDLE'

    @classmethod
    def next_frame(cls, context):
        # move to the next frame and render it
        if cls.mode == 'RENDER':
            # if rendering - retry after interval
            return cls._render_retry_interval
        elif cls.mode == 'IDLE':
            # if in idle
            next_frame = cls._get_next_frame(context=context)
            if next_frame is not None:
                # continue with the next frame
                context.scene.frame_set(next_frame)
                cls.mode = 'RENDER'  # current step in progress
                # execute render
                if not bpy.app.timers.is_registered(cls._render_frame):
                    bpy.app.timers.register(
                        cls._render_frame,
                        first_interval=cls._render_call_interval
                    )
                return cls._render_retry_interval
            else:
                # finish
                cls._finish(context=context)
                return None
        elif cls.mode == 'CANCEL':
            # manual finish by the user
            cls.stop(context=context)
            return None

    @classmethod
    def _render_frame(cls):
        # start render current frame
        rez = bpy.ops.render.render('INVOKE_DEFAULT', use_viewport=True)
        if rez == {'CANCELLED'}:
            # retry with timer
            return cls._render_call_interval

    @classmethod
    def _process_frames(cls, context, frames):
        # process frames
        if isinstance(frames, str):
            cls._frames = list(map(int, re.findall('\d+', frames)))
        elif isinstance(frames, list):
            cls._frames = frames
        if cls._frames:
            cls._frames.sort()
            cls._frames.append(None)    # None - last frame -> stop
        else:
            context.scene.frame_current = 0

    @classmethod
    def _get_next_frame(cls, context):
        # get next frame number
        next_frame = None
        if cls._frames:
            # by frames
            next_frame = cls._frames.pop(0)
        else:
            # all sequence
            if context.scene.frame_current + context.scene.frame_step <= context.scene.frame_end:
                next_frame = context.scene.frame_current + context.scene.frame_step
        return next_frame

    @classmethod
    def _on_render_complete(cls, *args):
        # render completed - current frame is rendered
        context = bpy.context
        # save data to frames_data
        pixels = cls._output_image(context=context).pixels[:]  # in RGBA format
        cls._frames_data.append(
            {
                'width': real_resolution(context=context)[0],
                'height': real_resolution(context=context)[1],
                'pixels': pixels,
                'len_rgba': len(pixels),
                'len_bytes': int(len(pixels) / 4),
                'frames_in_new_direction': cls._frames_in_new_direction(context=context)
            }
        )
        # idle for next frame render
        cls.mode = 'IDLE'

    @classmethod
    def _on_render_cancel(cls, *args):
        # render cancelled
        cls.mode = 'CANCEL'

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

    @staticmethod
    def _output_image(context):
        # get data output image (from Compositor Viewer Node)
        return next((image for image in context.blend_data.images
                     if image.name == 'Viewer Node'), None)

    @classmethod
    def _frames_in_new_direction(cls, context):
        # count frames in new direction if direction changes
        #   get information about changes from context.scene.sti_maker_props.change_direction_frames
        corner_frames = list(map(int, re.findall('\d+', context.scene.sti_maker_props.change_direction_frames)))
        # [17, 33]  for each 16 frames (16 * range + 1)
        corner_frames.append(context.scene.frame_start)
        corner_frames.append(context.scene.frame_end + 1)
        corner_frames.sort()    # [1, 17, 33, 49]
        if context.scene.frame_current not in corner_frames:
            frames_number = 0
        else:
            frame_index = corner_frames.index(context.scene.frame_current)
            frames_number = corner_frames[frame_index + 1] - context.scene.frame_current
        return frames_number
