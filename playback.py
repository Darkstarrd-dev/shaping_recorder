import os

import bmesh
import bpy

from . import export_utils
from . import graphics
from . import state
from . import view_utils
from .core.mesh_ops import compute_step_cache, interpolate_states_cached, update_mesh_vertices


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
