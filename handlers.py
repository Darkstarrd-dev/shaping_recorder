import bpy

from . import persistence
from . import state


@bpy.app.handlers.persistent
def load_post_handler(dummy):
    if bpy.context.scene:
        persistence.load_from_scene(bpy.context)


@bpy.app.handlers.persistent
def depsgraph_update_handler(scene, depsgraph):
    if state.is_recording or state.is_playing:
        return

    deleted = [name for name in state.object_records if name not in bpy.data.objects]
    for name in deleted:
        del state.object_records[name]
        if state.current_display_obj == name:
            state.current_display_obj = next(iter(state.object_records), None)
            persistence.sync_step_list(bpy.context)

    obj = bpy.context.active_object
    new_selection = obj.name if obj and obj.type == "MESH" else None

    if new_selection != state._prev_selection:
        state._prev_selection = new_selection

        if new_selection:
            if state.current_display_obj != new_selection:
                state.current_display_obj = new_selection
                persistence.sync_step_list(bpy.context)
