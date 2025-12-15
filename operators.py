import bpy
import bmesh
import json
import os
from . import state
from . import view_utils
from . import graphics
from . import export_utils
from bpy.app.translations import pgettext_iface as iface_


from .core.data import (
    serialize_view, deserialize_view,
    serialize_state, deserialize_state
)
from .core.mesh_ops import (
    get_mesh_hash, save_mesh_state, update_mesh_vertices,
    compute_step_cache, interpolate_states_cached
)



def ensure_object_mode(context, obj):
    if obj.mode != "OBJECT":
        context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")

def get_step_timing(context, step_index):
    settings = state.get_settings(context)
    for item in settings.step_items:
        if item.index == step_index and item.use_custom_timing:
            return item.cam_duration, item.mesh_duration
    return settings.global_cam_duration, settings.global_mesh_duration

def create_mesh_from_state(state_data, name="playback_mesh"):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for co in state_data["verts"]:
        bm.verts.new(co)
    bm.verts.ensure_lookup_table()
    for e in state_data["edges"]:
        if e[0] < len(bm.verts) and e[1] < len(bm.verts):
            try:
                bm.edges.new((bm.verts[e[0]], bm.verts[e[1]]))
            except ValueError:
                pass
    for f in state_data["faces"]:
        try:
            bm.faces.new([bm.verts[i] for i in f])
        except ValueError:
            pass
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def apply_state_to_object(obj, state_data, name_suffix="playback"):
    new_mesh = create_mesh_from_state(state_data, name=f"{obj.name}_{name_suffix}")
    old_mesh = obj.data
    obj.data = new_mesh
    if old_mesh and old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)

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



@bpy.app.handlers.persistent
def load_post_handler(dummy):
    if bpy.context.scene:
        load_from_scene(bpy.context)

@bpy.app.handlers.persistent
def depsgraph_update_handler(scene, depsgraph):
    if state.is_recording or state.is_playing:
        return

    
    deleted = [name for name in state.object_records if name not in bpy.data.objects]
    for name in deleted:
        del state.object_records[name]
        if state.current_display_obj == name:
            state.current_display_obj = next(iter(state.object_records), None)
            sync_step_list(bpy.context)

    
    obj = bpy.context.active_object
    new_selection = obj.name if obj and obj.type == "MESH" else None

    
    if new_selection != state._prev_selection:
        state._prev_selection = new_selection

        
        if new_selection:
            if state.current_display_obj != new_selection:
                state.current_display_obj = new_selection
                sync_step_list(bpy.context)
        
        
        
    



def jump_to_state_immediate(context, state_data):
    obj = state.get_recorded_object()
    if not obj:
        return
    ensure_object_mode(context, obj)
    apply_state_to_object(obj, state_data)
    view_utils.apply_view_state(context, state_data.get("view"))
    view_utils.apply_camera_state(context, state_data.get("camera"))

def start_interpolated_jump(context, source_state, target_state, step_index=0):
    obj = state.get_recorded_object()
    if not obj:
        return
    ensure_object_mode(context, obj)
    settings = state.get_settings(context)
    apply_state_to_object(obj, source_state)
    view_utils.apply_view_state(context, source_state.get("view"))
    cache = compute_step_cache(source_state, target_state)
    cam_dur, mesh_dur = get_step_timing(context, step_index)
    cam_changed = view_utils.view_state_changed(source_state.get("view"), target_state.get("view"))

    source_step_idx = step_index
    edge_indices = graphics.get_edge_indices_for_step(source_step_idx)
    graphics.update_mesh_new_edge_attribute(obj, edge_indices)
    graphics.update_edge_draw_coords(source_step_idx)

    state._jump_state = {
        "source": source_state,
        "target": target_state,
        "cache": cache,
        "elapsed": 0.0,
        "cam_duration": cam_dur if cam_changed else 0.0,
        "mesh_duration": mesh_dur,
        "source_step_idx": source_step_idx,
    }
    state.is_playing = True
    total_dur = state._jump_state["cam_duration"] + state._jump_state["mesh_duration"]
    interval = total_dur / max(1, settings.interp_steps)
    bpy.app.timers.register(lambda: jump_step(context), first_interval=interval)

def jump_step(context):
    if not state.is_playing or not state._jump_state:
        state.is_playing = False
        state._jump_state = None
        return None
    obj = state.get_recorded_object()
    if not obj:
        state.is_playing = False
        state._jump_state = None
        return None

    settings = state.get_settings(context)
    cam_duration = state._jump_state["cam_duration"]
    mesh_duration = state._jump_state["mesh_duration"]
    total_duration = cam_duration + mesh_duration
    interval = total_duration / max(1, settings.interp_steps)
    state._jump_state["elapsed"] += interval
    elapsed = state._jump_state["elapsed"]
    source = state._jump_state["source"]
    target = state._jump_state["target"]
    cache = state._jump_state["cache"]
    source_step_idx = state._jump_state.get("source_step_idx", -1)

    if cam_duration > 0 and elapsed < cam_duration:
        cam_t = elapsed / cam_duration
        mesh_t = 0.0
    else:
        cam_t = 1.0
        mesh_elapsed = elapsed - cam_duration if cam_duration > 0 else elapsed
        mesh_t = min(mesh_elapsed / max(mesh_duration, 1e-6), 1.0)

    view_utils.apply_view_state(context, view_utils.interpolate_view_state(source.get("view"), target.get("view"), cam_t))
    view_utils.apply_camera_state(context, view_utils.interpolate_camera_state(source.get("camera"), target.get("camera"), cam_t))

    if mesh_t > 0:
        new_verts, topo = interpolate_states_cached(source, target, mesh_t, cache)
        if not update_mesh_vertices(obj.data, new_verts):
            apply_state_to_object(obj, {"verts": new_verts, "edges": topo["edges"], "faces": topo["faces"]})
        
        graphics.update_edge_draw_coords(source_step_idx)

    if elapsed >= total_duration:
        
        
        

        state.is_playing = False
        state._jump_state = None
        return None
    return interval

def play_forward(context, export_frames=False, mode="range"):
    operation_history = state.get_current_history()
    initial_mesh = state.get_current_initial_mesh()

    if state.is_recording or state.is_playing or not operation_history:
        return

    obj = state.get_recorded_object()
    if not obj:
        print("No recorded target mesh")
        return

    ensure_object_mode(context, obj)
    settings = state.get_settings(context)
    state.is_exporting_frames = bool(export_frames)

    state._is_video_export = False
    state._temp_frame_dir = None
    if export_frames:
        scene = context.scene
        movie_formats = {"FFMPEG", "AVI_JPEG", "AVI_RAW"}
        if scene.render.image_settings.file_format in movie_formats:
            state._is_video_export = True
            base_path = bpy.path.abspath(scene.render.filepath)
            out_dir = os.path.dirname(base_path) if base_path else bpy.path.abspath("//")
            state._temp_frame_dir = os.path.join(out_dir, "_temp_frames")
            os.makedirs(state._temp_frame_dir, exist_ok=True)

    if mode == "start":
        start_idx = 0
        end_idx = len(operation_history) - 1
    elif mode == "active":
        idx = settings.active_step_index
        start_idx = max(0, idx - 1) if idx > 0 else 0
        end_idx = len(operation_history) - 1
    else:  
        start_idx = max(0, min(len(operation_history) - 1, settings.playback_start_step - 1))
        end_idx = (settings.playback_end_step - 1 if settings.playback_end_step > 0 else len(operation_history) - 1)
        end_idx = max(start_idx, min(len(operation_history) - 1, end_idx))

    state._playback_start_idx = start_idx
    state._playback_end_idx = end_idx

    if start_idx == 0:
        apply_state_to_object(obj, initial_mesh, name_suffix="start")
        view_utils.apply_view_state(context, initial_mesh.get("view"))
        view_utils.apply_camera_state(context, initial_mesh.get("camera"))
    else:
        prev_state = operation_history[start_idx - 1]
        apply_state_to_object(obj, prev_state, name_suffix="start")
        view_utils.apply_view_state(context, prev_state.get("view"))
        view_utils.apply_camera_state(context, prev_state.get("camera"))

    state.current_step = start_idx
    state.interp_progress = 0.0
    state._step_cache = None
    state._render_frame_idx = 0
    state.is_playing = True
    view_utils.lock_view_to_camera(context, True)
    toggle_overlays(True)

    interval = settings.step_duration / max(1, settings.interp_steps)
    bpy.app.timers.register(lambda: play_step(context), first_interval=interval)

def play_step(context):
    if not state.is_playing:
        return None

    obj = state.get_recorded_object()
    if not obj:
        stop_playing()
        return None

    operation_history = state.get_current_history()
    initial_mesh = state.get_current_initial_mesh()
    settings = state.get_settings(context)
    interp_steps = max(1, settings.interp_steps)
    interval = settings.step_duration / interp_steps

    state._is_auto_selecting = True
    settings.active_step_index = state.current_step + 1
    state._is_auto_selecting = False

    if state.current_step > state._playback_end_idx:
        stop_playing()
        return None

    target_state = operation_history[state.current_step]
    source_state = initial_mesh if state.current_step == 0 else operation_history[state.current_step - 1]
    source_step_idx = state.current_step

    cache_key = state.current_step
    if state._step_cache is None or state._step_cache.get("key") != cache_key:
        state._step_cache = compute_step_cache(source_state, target_state)
        state._step_cache["key"] = cache_key
        edge_indices = graphics.get_edge_indices_for_step(source_step_idx)
        graphics.update_mesh_new_edge_attribute(obj, edge_indices)
        graphics.update_edge_draw_coords(source_step_idx)

    state.interp_progress += interval
    cam_changed = view_utils.view_state_changed(source_state.get("view"), target_state.get("view")) or \
                  view_utils.camera_state_changed(source_state.get("camera"), target_state.get("camera"))

    step_cam_dur, step_mesh_dur = get_step_timing(context, state.current_step)
    cam_duration = step_cam_dur if cam_changed else 0.0
    mesh_duration = step_mesh_dur
    total_duration = cam_duration + mesh_duration
    elapsed = state.interp_progress

    if cam_changed and elapsed < cam_duration:
        cam_t = elapsed / cam_duration if cam_duration > 0.0 else 1.0
        mesh_t = 0.0
    else:
        cam_t = 1.0 if cam_changed else min(elapsed / mesh_duration, 1.0)
        mesh_elapsed = elapsed - cam_duration if cam_changed else elapsed
        mesh_t = min(mesh_elapsed / max(mesh_duration, 1e-6), 1.0)

    if elapsed >= total_duration:
        view_utils.apply_view_state(context, target_state.get("view"))
        view_utils.apply_camera_state(context, target_state.get("camera"))
        apply_state_to_object(obj, target_state)
        graphics.update_mesh_new_edge_attribute(obj, [])
        graphics.update_edge_draw_coords(None)
        export_utils.maybe_render_viewport_frame(context)

        state.current_step += 1
        state.interp_progress = 0.0
        state._step_cache = None
        return interval

    view_utils.apply_view_state(context, view_utils.interpolate_view_state(source_state.get("view"), target_state.get("view"), cam_t))
    view_utils.apply_camera_state(context, view_utils.interpolate_camera_state(source_state.get("camera"), target_state.get("camera"), cam_t))

    if not (cam_changed and elapsed < cam_duration):
        new_verts, topo_state = interpolate_states_cached(source_state, target_state, mesh_t, state._step_cache)
        if not update_mesh_vertices(obj.data, new_verts):
            apply_state_to_object(obj, {"verts": new_verts, "edges": topo_state["edges"], "faces": topo_state["faces"]})
        graphics.update_edge_draw_coords(source_step_idx)

    export_utils.maybe_render_viewport_frame(context)
    return interval

def stop_playing():
    was_video_export = state._is_video_export
    state.is_playing = False
    state._step_cache = None
    state.interp_progress = 0.0
    state.is_exporting_frames = False
    view_utils.lock_view_to_camera(bpy.context, False)
    toggle_overlays(False)
    if was_video_export:
        export_utils.finalize_video_export(bpy.context)
    state._total_export_frames = 0
    
    obj = state.get_recorded_object()
    if obj:
        graphics.update_mesh_new_edge_attribute(obj, [])
    graphics.update_edge_draw_coords(None)

def toggle_overlays(hide):
    screen = bpy.context.screen
    if not screen:
        return
    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            space.overlay.show_cursor = not hide
            space.overlay.show_floor = not hide
            space.overlay.show_edge_crease = hide

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

    
    
    if obj.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    bpy.ops.mesh.recorder_modal("INVOKE_DEFAULT")
    

def stop_recording():
    state.is_recording = False
    state.redo_history.clear()
    unlock_other_objects()
    rec = state.get_current_record()
    sync_step_list(bpy.context)
    save_to_scene(bpy.context)
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

                
                
                if obj.mode == 'SCULPT':
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
