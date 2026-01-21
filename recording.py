import bpy

from . import persistence
from . import state
from . import view_utils
from .core.mesh_ops import get_mesh_hash, save_mesh_state
from .playback import apply_state_to_object


def lock_other_objects(context, exclude_obj):
    state._locked_objects = []
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj != exclude_obj and not obj.hide_select:
            obj.hide_select = True
            state._locked_objects.append(obj.name)


def unlock_other_objects():
    for name in state._locked_objects:
        obj = bpy.data.objects.get(name)
        if obj:
            obj.hide_select = False
    state._locked_objects = []


def start_recording(context):
    if state.is_playing:
        return
    obj = context.active_object
    if not obj or obj.type != "MESH":
        return

    state.target_obj_name = obj.name
    state.current_display_obj = obj.name

    if obj.name in state.object_records:
        print(f"Resuming recording for {obj.name}...")
        rec = state.object_records[obj.name]
        history = rec["history"]

        if history:
            last_state = history[-1]
            apply_state_to_object(obj, last_state, name_suffix="resume")

            if last_state.get("view"):
                view_utils.apply_view_state(context, last_state.get("view"))
            if last_state.get("camera"):
                view_utils.apply_camera_state(context, last_state.get("camera"))

            state.last_hash = get_mesh_hash(obj)
        else:
            state.last_hash = get_mesh_hash(obj)

        state.redo_history.clear()

    else:
        print(f"Starting new recording for {obj.name}...")

        initial_mesh = save_mesh_state(obj)
        initial_mesh["view"] = view_utils.save_view_state(context)
        initial_mesh["camera"] = view_utils.save_camera_state(context)

        state.initial_hash = get_mesh_hash(obj)
        state.last_hash = state.initial_hash
        initial_mesh["hash"] = state.initial_hash

        state.object_records[obj.name] = {
            "initial_mesh": initial_mesh,
            "history": [],
            "redo": [],
        }
        state.redo_history.clear()

    state.is_recording = True
    lock_other_objects(context, obj)

    if obj.mode != "EDIT":
        bpy.ops.object.mode_set(mode="EDIT")

    bpy.ops.mesh.recorder_modal("INVOKE_DEFAULT")


def stop_recording():
    state.is_recording = False
    state.redo_history.clear()
    unlock_other_objects()
    state.get_current_record()
    persistence.sync_step_list(bpy.context)
    persistence.save_to_scene(bpy.context)
    state.target_obj_name = None


class MeshRecorderModal(bpy.types.Operator):
    bl_idname = "mesh.recorder_modal"
    bl_label = "Mesh Recorder Modal"
    bl_options = {"REGISTER"}

    _timer = None
    _stable_count = 0
    _pending_hash = None

    def modal(self, context, event):
        if not state.is_recording:
            self.cancel(context)
            return {"CANCELLED"}

        if event.type == "TIMER":
            obj = context.active_object
            if obj and obj.type == "MESH" and obj.name == state.target_obj_name:
                rec = state.object_records.get(state.target_obj_name)
                if not rec:
                    return {"PASS_THROUGH"}
                operation_history = rec["history"]

                data_source = obj

                if obj.mode == "SCULPT":
                    is_dyntopo = False
                    try:
                        if obj.use_dynamic_topology_sculpting:
                            is_dyntopo = True
                    except AttributeError:
                        pass

                    if is_dyntopo:
                        depsgraph = context.evaluated_depsgraph_get()
                        data_source = obj.evaluated_get(depsgraph)

                current_hash = get_mesh_hash(data_source)

                if current_hash != state.last_hash:
                    if current_hash == self._pending_hash:
                        self._stable_count += 1
                        if self._stable_count >= 3:
                            base_hash = state.initial_hash if state.initial_hash is not None else state.last_hash
                            history_hashes = [base_hash] + [s.get("hash") for s in operation_history]

                            if current_hash in history_hashes:
                                match_idx = history_hashes.index(current_hash)
                                keep_len = max(0, match_idx)
                                if keep_len < len(operation_history):
                                    removed = operation_history[keep_len:]
                                    state.redo_history[:] = removed + state.redo_history
                                    del operation_history[keep_len:]
                                state.last_hash = current_hash

                            else:
                                redo_hashes = [s.get("hash") for s in state.redo_history]
                                if current_hash in redo_hashes:
                                    redo_idx = redo_hashes.index(current_hash)
                                    restored = state.redo_history[: redo_idx + 1]
                                    operation_history.extend(restored)
                                    del state.redo_history[: redo_idx + 1]
                                    state.last_hash = current_hash
                                else:
                                    state.redo_history.clear()

                                    s = save_mesh_state(data_source)

                                    s["view"] = view_utils.save_view_state(context)
                                    s["camera"] = view_utils.save_camera_state(context)
                                    s["hash"] = current_hash
                                    operation_history.append(s)
                                    state.last_hash = current_hash

                            self._stable_count = 0
                            self._pending_hash = None
                    else:
                        self._pending_hash = current_hash
                        self._stable_count = 1

        return {"PASS_THROUGH"}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        self._stable_count = 0
        self._pending_hash = None
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
