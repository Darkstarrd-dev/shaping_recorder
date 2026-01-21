import json

import bpy

from . import state
from ..core.data import deserialize_state, serialize_state


def sync_step_list(context, keep_index=None):
    settings = state.get_settings(context)
    settings.step_items.clear()
    initial_mesh = state.get_current_initial_mesh()
    operation_history = state.get_current_history()
    if not initial_mesh:
        return
    item = settings.step_items.add()
    item.index = -1
    for i in range(len(operation_history)):
        item = settings.step_items.add()
        item.index = i
    state._is_auto_selecting = True
    if keep_index is not None:
        settings.active_step_index = min(keep_index, len(settings.step_items) - 1)
    else:
        settings.active_step_index = 0
    state._is_auto_selecting = False


def save_to_scene(context):
    scene = context.scene
    settings = state.get_settings(context)
    data = {
        "object_records": {},
        "current_display_obj": state.current_display_obj,
        "step_timing": {},
    }
    for obj_name, rec in state.object_records.items():
        data["object_records"][obj_name] = {
            "initial_mesh": serialize_state(rec["initial_mesh"]),
            "history": [serialize_state(s) for s in rec["history"]],
        }
    if state.current_display_obj:
        timing_list = []
        for item in settings.step_items:
            timing_list.append({
                "use_custom": item.use_custom_timing,
                "cam": item.cam_duration,
                "mesh": item.mesh_duration,
                "marked_edges": item.marked_edge_indices,
                "show_edges": item.show_changed_edges,
            })
        data["step_timing"][state.current_display_obj] = timing_list
    scene["mesh_recorder_data"] = json.dumps(data)


def load_from_scene(context):
    scene = context.scene
    if "mesh_recorder_data" not in scene:
        return
    try:
        data = json.loads(scene["mesh_recorder_data"])
        if "object_records" in data:
            state.object_records.clear()
            for obj_name, rec in data.get("object_records", {}).items():
                if obj_name not in bpy.data.objects:
                    continue
                state.object_records[obj_name] = {
                    "initial_mesh": deserialize_state(rec.get("initial_mesh")),
                    "history": [deserialize_state(s) for s in rec.get("history", [])],
                    "redo": [],
                }
            state.current_display_obj = data.get("current_display_obj")
            if state.current_display_obj and state.current_display_obj not in state.object_records:
                state.current_display_obj = next(iter(state.object_records), None)
        else:
            state.object_records.clear()
            old_name = data.get("target_obj_name")
            if old_name and old_name in bpy.data.objects:
                state.object_records[old_name] = {
                    "initial_mesh": deserialize_state(data.get("initial_mesh")),
                    "history": [deserialize_state(s) for s in data.get("operation_history", [])],
                    "redo": [],
                }
                state.current_display_obj = old_name
        sync_step_list(context)

        settings = state.get_settings(context)
        step_timing = data.get("step_timing", {})
        if state.current_display_obj and state.current_display_obj in step_timing:
            timing_list = step_timing[state.current_display_obj]
            for i, timing in enumerate(timing_list):
                if i < len(settings.step_items):
                    settings.step_items[i].use_custom_timing = timing.get("use_custom", False)
                    settings.step_items[i].cam_duration = timing.get("cam", 0.5)
                    settings.step_items[i].mesh_duration = timing.get("mesh", 0.5)
                    settings.step_items[i].marked_edge_indices = timing.get("marked_edges", "")
                    settings.step_items[i].show_changed_edges = timing.get("show_edges", False)
    except Exception as e:
        print(f"Failed to load recorder data: {e}")
