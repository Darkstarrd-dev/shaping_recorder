import bpy
import bmesh
import json

from bpy.app.translations import pgettext_iface as iface_

from ..utils import graphics
from ..data import state
from ..utils import view as view_utils
from ..utils.handlers import depsgraph_update_handler, load_post_handler
from ..data.persistence import load_from_scene, save_to_scene, sync_step_list
from .playback import (
    jump_step,
    jump_to_state_immediate,
    play_forward,
    play_step,
    start_interpolated_jump,
    stop_playing,
)
from .recording import (
    MeshRecorderModal,
    lock_other_objects,
    start_recording,
    stop_recording,
    unlock_other_objects,
)


def _require_active_step(operator, context):
    settings = state.get_settings(context)
    if not settings.step_items:
        operator.report({"INFO"}, iface_("Select a step from the list"))
        return False
    if settings.active_step_index < 0 or settings.active_step_index >= len(settings.step_items):
        operator.report({"INFO"}, iface_("Select a step from the list"))
        return False
    item = settings.step_items[settings.active_step_index]
    if item.index < 0:
        operator.report({"INFO"}, iface_("Select a step from the list"))
        return False
    return True


class StartRecordingOperator(bpy.types.Operator):
    bl_idname = "mesh.start_recording"
    bl_label = "Start Recording"
    bl_options = {"REGISTER"}
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH" and not state.is_recording and not state.is_playing
    def execute(self, context):
        start_recording(context)
        return {"FINISHED"}

class StopRecordingOperator(bpy.types.Operator):
    bl_idname = "mesh.stop_recording"
    bl_label = "Stop Recording"
    bl_options = {"REGISTER"}
    @classmethod
    def poll(cls, context):
        return state.is_recording
    def execute(self, context):
        stop_recording()
        return {"FINISHED"}

class StopPlayingOperator(bpy.types.Operator):
    bl_idname = "mesh.stop_playing"
    bl_label = "Stop Playing"
    bl_options = {"REGISTER"}
    @classmethod
    def poll(cls, context):
        return state.is_playing
    def execute(self, context):
        stop_playing()
        return {"FINISHED"}

class DeleteStepOperator(bpy.types.Operator):
    bl_idname = "mesh.delete_recorder_step"
    bl_label = "Delete Step"
    bl_options = {"REGISTER", "UNDO"}
    step_index: bpy.props.IntProperty()
    @classmethod
    def poll(cls, context):
        return not state.is_recording and not state.is_playing
    def execute(self, context):
        idx = self.step_index
        operation_history = state.get_current_history()
        if idx < 0 or idx >= len(operation_history):
            return {"CANCELLED"}
        settings = state.get_settings(context)
        current_index = settings.active_step_index
        timing_data = None
        for item in settings.step_items:
            if item.index == idx:
                timing_data = {"use_custom": item.use_custom_timing, "cam": item.cam_duration, "mesh": item.mesh_duration}
                break
        state._deleted_step = {
            "index": idx,
            "state": operation_history[idx],
            "timing": timing_data,
            "obj_name": state.current_display_obj,
        }
        del operation_history[idx]
        sync_step_list(context, keep_index=current_index)
        save_to_scene(context)
        return {"FINISHED"}

class RestoreStepOperator(bpy.types.Operator):
    bl_idname = "mesh.restore_recorder_step"
    bl_label = "Restore Deleted Step"
    bl_options = {"REGISTER", "UNDO"}
    @classmethod
    def poll(cls, context):
        return state._deleted_step is not None and not state.is_recording and not state.is_playing and state._deleted_step.get("obj_name") == state.current_display_obj
    def execute(self, context):
        idx = state._deleted_step["index"]
        s = state._deleted_step["state"]
        timing = state._deleted_step.get("timing")
        operation_history = state.get_current_history()
        operation_history.insert(idx, s)
        sync_step_list(context)
        if timing:
            settings = state.get_settings(context)
            for item in settings.step_items:
                if item.index == idx:
                    item.use_custom_timing = timing.get("use_custom", False)
                    item.cam_duration = timing.get("cam", 0.5)
                    item.mesh_duration = timing.get("mesh", 0.5)
                    break
        state._deleted_step = None
        save_to_scene(context)
        return {"FINISHED"}

class ResetStepViewOperator(bpy.types.Operator):
    bl_idname = "mesh.reset_step_view"
    bl_label = "Reset Camera"
    bl_options = {"REGISTER"}
    @classmethod
    def poll(cls, context):
        if state.is_recording or state.is_playing or state._is_resetting_view:
            return False
        settings = state.get_settings(context)
        return settings.step_items and settings.step_items[settings.active_step_index].index >= 0
    def execute(self, context):
        state._is_resetting_view = True
        return {"FINISHED"}

class ConfirmStepViewOperator(bpy.types.Operator):
    bl_idname = "mesh.confirm_step_view"
    bl_label = "Confirm Camera"
    bl_options = {"REGISTER", "UNDO"}
    @classmethod
    def poll(cls, context):
        return state._is_resetting_view
    def execute(self, context):
        settings = state.get_settings(context)
        item = settings.step_items[settings.active_step_index]
        operation_history = state.get_current_history()
        operation_history[item.index]["view"] = view_utils.save_view_state(context)
        save_to_scene(context)
        state._is_resetting_view = False
        return {"FINISHED"}

class PlayUnifiedOperator(bpy.types.Operator):
    bl_idname = "mesh.play_unified"
    bl_label = "Play"
    bl_options = {"REGISTER"}
    @classmethod
    def poll(cls, context):
        return not state.is_recording and not state.is_playing and bool(state.get_current_history())
    def execute(self, context):
        settings = state.get_settings(context)
        if settings.playback_mode == "ACTIVE" and not _require_active_step(self, context):
            return {"CANCELLED"}
        mode = {"START": "start", "ACTIVE": "active", "RANGE": "range"}.get(settings.playback_mode, "range")
        play_forward(context, export_frames=False, mode=mode)
        return {"FINISHED"}

class RecordUnifiedOperator(bpy.types.Operator):
    bl_idname = "mesh.record_unified"
    bl_label = "Record"
    bl_options = {"REGISTER"}
    @classmethod
    def poll(cls, context):
        return not state.is_recording and not state.is_playing and bool(state.get_current_history())
    def execute(self, context):
        settings = state.get_settings(context)
        if settings.playback_mode == "ACTIVE" and not _require_active_step(self, context):
            return {"CANCELLED"}
        mode = {"START": "start", "ACTIVE": "active", "RANGE": "range"}.get(settings.playback_mode, "range")
        play_forward(context, export_frames=True, mode=mode)
        return {"FINISHED"}

class SetStartStepOperator(bpy.types.Operator):
    bl_idname = "mesh.set_start_step"
    bl_label = "Set Start"
    bl_options = {"REGISTER"}
    @classmethod
    def poll(cls, context):
        return not state.is_recording and not state.is_playing and state.get_settings(context).step_items
    def execute(self, context):
        settings = state.get_settings(context)
        item = settings.step_items[settings.active_step_index]
        new_start = item.index + 1
        if settings.playback_end_step == 0 or new_start <= settings.playback_end_step:
            settings.playback_start_step = new_start
        return {"FINISHED"}

class SetEndStepOperator(bpy.types.Operator):
    bl_idname = "mesh.set_end_step"
    bl_label = "Set End"
    bl_options = {"REGISTER"}
    @classmethod
    def poll(cls, context):
        return not state.is_recording and not state.is_playing and state.get_settings(context).step_items
    def execute(self, context):
        settings = state.get_settings(context)
        item = settings.step_items[settings.active_step_index]
        new_end = item.index + 1
        if new_end >= settings.playback_start_step:
            settings.playback_end_step = new_end
        return {"FINISHED"}

class ToggleChangedEdgesOperator(bpy.types.Operator):
    bl_idname = "mesh.toggle_changed_edges"
    bl_label = "Toggle Highlighted Edges"
    bl_options = {"REGISTER", "UNDO"}
    step_index: bpy.props.IntProperty()
    @classmethod
    def poll(cls, context):
        return not state.is_recording and not state.is_playing and state.current_display_obj
    def execute(self, context):
        settings = state.get_settings(context)
        item = next((it for it in settings.step_items if it.index == self.step_index), None)
        if not item: return {"CANCELLED"}
        item.show_changed_edges = not item.show_changed_edges
        target_idx = settings.step_items[settings.active_step_index].index if settings.step_items else -1
        source_idx = target_idx
        edge_indices = graphics.get_edge_indices_for_step(source_idx)
        obj = state.get_recorded_object()
        if obj: graphics.update_mesh_new_edge_attribute(obj, edge_indices)
        graphics.update_edge_draw_coords(source_idx)
        return {"FINISHED"}

class MarkEdgeOperator(bpy.types.Operator):
    bl_idname = "mesh.mark_new_edge"
    bl_label = "Mark Edge"
    bl_options = {"REGISTER"}
    @classmethod
    def poll(cls, context):
        if state.is_recording or state.is_playing or state._is_marking_edge: return False
        if not state.current_display_obj: return False
        return True
    def execute(self, context):
        settings = state.get_settings(context)
        item = settings.step_items[settings.active_step_index]
        state._marking_step_index = item.index
        state._is_marking_edge = True
        obj = state.get_recorded_object()
        if obj:
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='EDGE')
            bpy.ops.mesh.select_all(action='DESELECT')
        return {"FINISHED"}

class ConfirmEdgeOperator(bpy.types.Operator):
    bl_idname = "mesh.confirm_new_edge"
    bl_label = "Confirm"
    bl_options = {"REGISTER", "UNDO"}
    @classmethod
    def poll(cls, context):
        return state._is_marking_edge
    def execute(self, context):
        obj = state.get_recorded_object()
        if not obj or obj.mode != 'EDIT':
            state._is_marking_edge = False
            state._marking_step_index = -1
            return {"CANCELLED"}
        bm = bmesh.from_edit_mesh(obj.data)
        edge_indices = [[e.verts[0].index, e.verts[1].index] for e in bm.edges if e.select]
        bpy.ops.object.mode_set(mode='OBJECT')
        settings = state.get_settings(context)
        for item in settings.step_items:
            if item.index == state._marking_step_index:
                item.marked_edge_indices = json.dumps(edge_indices)
                item.show_changed_edges = True
                break
        target_idx = settings.step_items[settings.active_step_index].index if settings.step_items else -1
        source_idx = target_idx
        display_edges = graphics.get_edge_indices_for_step(source_idx)
        graphics.update_mesh_new_edge_attribute(obj, display_edges)
        graphics.update_edge_draw_coords(source_idx)
        save_to_scene(context)
        state._is_marking_edge = False
        state._marking_step_index = -1
        return {"FINISHED"}


class PlayFromActiveOperator(bpy.types.Operator):
    bl_idname = "mesh.play_from_active"
    bl_label = "Play"
    bl_options = {"REGISTER"}
    @classmethod
    def poll(cls, context): return PlayUnifiedOperator.poll(context)
    def execute(self, context):
        if not _require_active_step(self, context):
            return {"CANCELLED"}
        play_forward(context, export_frames=False, mode="active")
        return {"FINISHED"}

class PlayFromRangeOperator(bpy.types.Operator):
    bl_idname = "mesh.play_from_range"
    bl_label = "Play"
    bl_options = {"REGISTER"}
    @classmethod
    def poll(cls, context): return PlayUnifiedOperator.poll(context)
    def execute(self, context):
        play_forward(context, export_frames=False, mode="range")
        return {"FINISHED"}

class PlayFromStartOperator(bpy.types.Operator):
    bl_idname = "mesh.play_from_start"
    bl_label = "Play"
    bl_options = {"REGISTER"}
    @classmethod
    def poll(cls, context): return PlayUnifiedOperator.poll(context)
    def execute(self, context):
        play_forward(context, export_frames=False, mode="start")
        return {"FINISHED"}

class RecordFromActiveOperator(bpy.types.Operator):
    bl_idname = "mesh.record_from_active"
    bl_label = "Record"
    bl_options = {"REGISTER"}
    @classmethod
    def poll(cls, context): return RecordUnifiedOperator.poll(context)
    def execute(self, context):
        if not _require_active_step(self, context):
            return {"CANCELLED"}
        play_forward(context, export_frames=True, mode="active")
        return {"FINISHED"}

class RecordFromRangeOperator(bpy.types.Operator):
    bl_idname = "mesh.record_from_range"
    bl_label = "Record"
    bl_options = {"REGISTER"}
    @classmethod
    def poll(cls, context): return RecordUnifiedOperator.poll(context)
    def execute(self, context):
        play_forward(context, export_frames=True, mode="range")
        return {"FINISHED"}

class RecordFromStartOperator(bpy.types.Operator):
    bl_idname = "mesh.record_from_start"
    bl_label = "Record"
    bl_options = {"REGISTER"}
    @classmethod
    def poll(cls, context): return RecordUnifiedOperator.poll(context)
    def execute(self, context):
        play_forward(context, export_frames=True, mode="start")
        return {"FINISHED"}
