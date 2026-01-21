import json
import os
from array import array

import bmesh
import bpy
from bpy.app.translations import pgettext_iface as iface_
from mathutils import kdtree


from .translations import translations
from .core.data import (
    serialize_view, deserialize_view,
    serialize_camera, deserialize_camera,
    serialize_state, deserialize_state
)
from .core.mesh_ops import (
    get_mesh_hash, save_mesh_state, update_mesh_vertices,
    build_vertex_mapping, compute_step_cache, interpolate_states_cached
)



object_records = {}  
current_display_obj = None  
redo_history = []
initial_hash = None
is_recording = False
is_playing = False
is_exporting_frames = False
current_step = 0
last_hash = None
target_obj_name = None  
interp_progress = 0.0
_locked_objects = []  

_step_cache = None
_highlight_obj_name = "__MeshRecorder_NewEdges"
_render_frame_idx = 0
_view_lock_state = {}
_video_render_handler = None
_prev_render_settings = None
_playback_start_idx = 0
_playback_end_idx = -1
_jump_state = None
_deleted_step = None
_is_resetting_view = False
_is_auto_selecting = False
_prev_selection = None
_temp_frame_dir = None
_is_video_export = False
_total_export_frames = 0
_vse_backup = None
_edge_draw_handler = None
_current_edge_coords = []
_is_marking_edge = False
_marking_step_index = -1


def update_mesh_new_edge_attribute(obj, edge_indices):
    """Update new_edge attribute on main mesh. edge_indices: list of [v0, v1] pairs."""
    mesh = obj.data
    if not edge_indices:
        if "new_edge" in mesh.attributes:
            mesh.attributes.remove(mesh.attributes["new_edge"])
        return

    marked = {tuple(sorted(e)) for e in edge_indices}
    values = [tuple(sorted([e.vertices[0], e.vertices[1]])) in marked for e in mesh.edges]

    if "new_edge" not in mesh.attributes:
        mesh.attributes.new("new_edge", 'BOOLEAN', 'EDGE')
    mesh.attributes["new_edge"].data.foreach_set("value", values)
    mesh.update()


def update_edge_draw_coords(step_index=None):
    """Update coordinates for GPU drawing based on specified step.

    Args:
        step_index: The step index to get edge data from. If None, clears edges.
    """
    global _current_edge_coords
    _current_edge_coords = []

    if step_index is None or step_index < 0:
        return

    if not current_display_obj:
        return

    settings = get_settings(bpy.context)
    if not settings.step_items:
        return

    
    item = None
    for it in settings.step_items:
        if it.index == step_index:
            item = it
            break

    if not item or not item.show_changed_edges or not item.marked_edge_indices:
        return

    obj = get_recorded_object()
    if not obj:
        return

    try:
        edge_indices = json.loads(item.marked_edge_indices)
    except:
        return

    mesh = obj.data
    mat = obj.matrix_world
    for v0_idx, v1_idx in edge_indices:
        if v0_idx < len(mesh.vertices) and v1_idx < len(mesh.vertices):
            v0 = mat @ mesh.vertices[v0_idx].co
            v1 = mat @ mesh.vertices[v1_idx].co
            _current_edge_coords.extend([v0, v1])


def get_edge_indices_for_step(step_index):
    """Get marked edge indices for a specific step."""
    if step_index < 0:
        return []
    settings = get_settings(bpy.context)
    for item in settings.step_items:
        if item.index == step_index and item.show_changed_edges and item.marked_edge_indices:
            try:
                return json.loads(item.marked_edge_indices)
            except:
                pass
    return []


def draw_changed_edges():
    """GPU draw handler for changed edges with glow effect."""
    global _current_edge_coords
    if not _current_edge_coords:
        return

    import gpu
    from gpu_extras.batch import batch_for_shader

    settings = get_settings(bpy.context)
    color = tuple(settings.edge_color)
    width = settings.edge_width
    glow = settings.edge_glow

    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": _current_edge_coords})

    gpu.state.blend_set('ALPHA')

    
    if glow > 0:
        layers = int(glow * 2) + 1
        for i in range(layers, 0, -1):
            alpha = color[3] * (1 - i / (layers + 1)) * 0.5
            w = width + i * 2
            shader.uniform_float("viewportSize", gpu.state.viewport_get()[2:])
            shader.uniform_float("lineWidth", w)
            shader.uniform_float("color", (color[0], color[1], color[2], alpha))
            batch.draw(shader)

    
    shader.uniform_float("viewportSize", gpu.state.viewport_get()[2:])
    shader.uniform_float("lineWidth", width)
    shader.uniform_float("color", color)
    batch.draw(shader)

    gpu.state.blend_set('NONE')


def save_to_scene(context):
    global object_records, current_display_obj
    scene = context.scene
    settings = get_settings(context)
    data = {
        "object_records": {},
        "current_display_obj": current_display_obj,
        "step_timing": {},
    }
    for obj_name, rec in object_records.items():
        data["object_records"][obj_name] = {
            "initial_mesh": serialize_state(rec["initial_mesh"]),
            "history": [serialize_state(s) for s in rec["history"]],
        }
    
    if current_display_obj:
        timing_list = []
        for item in settings.step_items:
            timing_list.append({
                "use_custom": item.use_custom_timing,
                "cam": item.cam_duration,
                "mesh": item.mesh_duration,
                "marked_edges": item.marked_edge_indices,
                "show_edges": item.show_changed_edges,
            })
        data["step_timing"][current_display_obj] = timing_list
    scene["mesh_recorder_data"] = json.dumps(data)


def load_from_scene(context):
    global object_records, current_display_obj
    scene = context.scene
    if "mesh_recorder_data" not in scene:
        return
    try:
        data = json.loads(scene["mesh_recorder_data"])
        
        if "object_records" in data:
            object_records.clear()
            for obj_name, rec in data.get("object_records", {}).items():
                
                if obj_name not in bpy.data.objects:
                    continue
                object_records[obj_name] = {
                    "initial_mesh": deserialize_state(rec.get("initial_mesh")),
                    "history": [deserialize_state(s) for s in rec.get("history", [])],
                    "redo": [],
                }
            current_display_obj = data.get("current_display_obj")
            if current_display_obj and current_display_obj not in object_records:
                current_display_obj = next(iter(object_records), None)
        else:
            
            object_records.clear()
            old_name = data.get("target_obj_name")
            if old_name and old_name in bpy.data.objects:
                object_records[old_name] = {
                    "initial_mesh": deserialize_state(data.get("initial_mesh")),
                    "history": [deserialize_state(s) for s in data.get("operation_history", [])],
                    "redo": [],
                }
                current_display_obj = old_name
        sync_step_list(context)
        
        settings = get_settings(context)
        step_timing = data.get("step_timing", {})
        if current_display_obj and current_display_obj in step_timing:
            timing_list = step_timing[current_display_obj]
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
    """Handle selection changes and object deletion"""
    global current_display_obj, object_records, _prev_selection

    if is_recording or is_playing:
        return

    
    deleted = [name for name in object_records if name not in bpy.data.objects]
    for name in deleted:
        del object_records[name]
        if current_display_obj == name:
            current_display_obj = next(iter(object_records), None)
            sync_step_list(bpy.context)

    
    obj = bpy.context.active_object
    new_selection = obj.name if obj and obj.type == "MESH" else None

    if new_selection != _prev_selection:
        _prev_selection = new_selection
        
        if new_selection and new_selection in object_records:
            if current_display_obj != new_selection:
                current_display_obj = new_selection
                sync_step_list(bpy.context)


def get_current_record():
    """Get the record for current_display_obj"""
    if not current_display_obj or current_display_obj not in object_records:
        return None
    return object_records[current_display_obj]


def get_current_history():
    """Get operation_history for current display object"""
    rec = get_current_record()
    return rec["history"] if rec else []


def get_current_initial_mesh():
    """Get initial_mesh for current display object"""
    rec = get_current_record()
    return rec["initial_mesh"] if rec else None


def get_recorded_object():
    """Get the object for current display"""
    if not current_display_obj:
        return None
    obj = bpy.data.objects.get(current_display_obj)
    if obj and obj.type == "MESH":
        return obj
    return None


def save_view_state(context):
    screen = context.screen or bpy.context.screen
    if not screen:
        return None
    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            r3d = space.region_3d
            if r3d:
                return {
                    "view_perspective": r3d.view_perspective,
                    "view_location": r3d.view_location.copy(),
                    "view_rotation": r3d.view_rotation.copy(),
                    "view_distance": float(r3d.view_distance),
                }
    return None


def interpolate_view_state(state1, state2, t):
    if not state1 and not state2:
        return None
    if not state1:
        return {
            "view_perspective": state2.get("view_perspective", "PERSP"),
            "view_location": state2["view_location"].copy(),
            "view_rotation": state2["view_rotation"].copy(),
            "view_distance": float(state2.get("view_distance", 0.0)),
        }
    if not state2:
        return {
            "view_perspective": state1.get("view_perspective", "PERSP"),
            "view_location": state1["view_location"].copy(),
            "view_rotation": state1["view_rotation"].copy(),
            "view_distance": float(state1.get("view_distance", 0.0)),
        }

    loc = state1["view_location"].lerp(state2["view_location"], t)
    rot = state1["view_rotation"].slerp(state2["view_rotation"], t)
    dist1 = float(state1.get("view_distance", 0.0))
    dist2 = float(state2.get("view_distance", 0.0))
    dist = dist1 + (dist2 - dist1) * t
    perspective = state2.get(
        "view_perspective", state1.get("view_perspective", "PERSP")
    )
    return {
        "view_perspective": perspective,
        "view_location": loc,
        "view_rotation": rot,
        "view_distance": dist,
    }


def view_state_changed(state1, state2, loc_eps=1e-5, dist_eps=1e-5, ang_eps=1e-4):
    if state1 is None and state2 is None:
        return False
    if state1 is None or state2 is None:
        return True

    try:
        if (state1["view_location"] - state2["view_location"]).length > loc_eps:
            return True
        if (
            abs(
                float(state1.get("view_distance", 0.0))
                - float(state2.get("view_distance", 0.0))
            )
            > dist_eps
        ):
            return True
        q1 = state1["view_rotation"]
        q2 = state2["view_rotation"]
        if q1.rotation_difference(q2).angle > ang_eps:
            return True
        if state1.get("view_perspective") != state2.get("view_perspective"):
            return True
    except Exception:
        return True

    return False


def camera_state_changed(state1, state2, loc_eps=1e-5, ang_eps=1e-4):
    if state1 is None and state2 is None:
        return False
    if state1 is None or state2 is None:
        return True
    try:
        if (state1["location"] - state2["location"]).length > loc_eps:
            return True
        q1 = state1["rotation"]
        q2 = state2["rotation"]
        if q1.rotation_difference(q2).angle > ang_eps:
            return True
    except Exception:
        return True
    return False


def apply_view_state(context, state):
    if not state:
        return
    screen = context.screen or bpy.context.screen
    if not screen:
        return
    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            r3d = space.region_3d
            if not r3d:
                continue
            r3d.view_perspective = state.get("view_perspective", r3d.view_perspective)
            r3d.view_location = state["view_location"]
            r3d.view_rotation = state["view_rotation"]
            r3d.view_distance = state.get("view_distance", r3d.view_distance)



def save_camera_state(context):
    cam = context.scene.camera
    if not cam:
        return None
    if cam.rotation_mode == "QUATERNION":
        rot = cam.rotation_quaternion.copy()
    else:
        rot = cam.rotation_euler.to_quaternion()
    return {"location": cam.location.copy(), "rotation": rot}


def interpolate_camera_state(state1, state2, t):
    if not state1 and not state2:
        return None
    if not state1:
        return {
            "location": state2["location"].copy(),
            "rotation": state2["rotation"].copy(),
        }
    if not state2:
        return {
            "location": state1["location"].copy(),
            "rotation": state1["rotation"].copy(),
        }
    loc = state1["location"].lerp(state2["location"], t)
    rot = state1["rotation"].slerp(state2["rotation"], t)
    return {"location": loc, "rotation": rot}


def apply_camera_state(context, state):
    cam = context.scene.camera
    if not cam or not state:
        return
    cam.location = state["location"]
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = state["rotation"]


def lock_view_to_camera(context, lock):
    global _view_lock_state
    screen = context.screen or bpy.context.screen
    if not screen:
        return

    if lock:
        _view_lock_state.clear()
        for area in screen.areas:
            if area.type == "VIEW_3D":
                space = area.spaces.active
                r3d = space.region_3d
                if not r3d:
                    continue
                _view_lock_state[area.as_pointer()] = {
                    "view_perspective": r3d.view_perspective,
                    "view_location": r3d.view_location.copy(),
                    "view_rotation": r3d.view_rotation.copy(),
                    "view_distance": r3d.view_distance,
                }
        return

    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            r3d = space.region_3d
            if not r3d:
                continue
            state = _view_lock_state.get(area.as_pointer())
            if not state:
                continue
            r3d.view_perspective = state["view_perspective"]
            r3d.view_location = state["view_location"]
            r3d.view_rotation = state["view_rotation"]
            r3d.view_distance = state.get("view_distance", r3d.view_distance)
    _view_lock_state.clear()


def maybe_render_viewport_frame(context):
    global _render_frame_idx, is_exporting_frames, _total_export_frames
    if not is_exporting_frames:
        return

    settings = get_settings(context)
    scene = context.scene

    
    if _is_video_export and _temp_frame_dir:
        out_dir = _temp_frame_dir
    else:
        base_path = bpy.path.abspath(scene.render.filepath)
        out_dir = os.path.dirname(base_path) if base_path else bpy.path.abspath("//")
    os.makedirs(out_dir, exist_ok=True)

    def _ext_from_format(fmt):
        mapping = {
            "PNG": ".png",
            "JPEG": ".jpg",
            "JPEG2000": ".jp2",
            "OPEN_EXR": ".exr",
            "OPEN_EXR_MULTILAYER": ".exr",
            "TIFF": ".tif",
            "TARGA": ".tga",
            "TARGA_RAW": ".tga",
            "BMP": ".bmp",
            "WEBP": ".webp",
            "HDR": ".hdr",
            "DPX": ".dpx",
            "CINEON": ".cin",
            "IRIS": ".rgb",
        }
        return mapping.get(fmt, ".png")

    prev_path = scene.render.filepath
    prev_format = scene.render.image_settings.file_format
    prev_color_mode = scene.render.image_settings.color_mode

    
    target_format = "PNG" if _is_video_export else prev_format
    movie_formats = {"FFMPEG", "AVI_JPEG", "AVI_RAW"}
    if target_format in movie_formats:
        target_format = "PNG"

    ext = _ext_from_format(target_format)
    filepath = os.path.join(
        out_dir, f"{settings.render_prefix}_{_render_frame_idx:04d}{ext}"
    )

    try:
        if _is_video_export:
            
            if settings.export_render_mode == "FINAL":
                bpy.ops.render.render(write_still=False)
            else:
                bpy.ops.render.opengl(write_still=False, view_context=True)
            
            img = bpy.data.images.get("Render Result")
            if img:
                img.save_render(filepath, scene=scene)
        else:
            
            scene.render.filepath = filepath
            if target_format not in {"FFMPEG", "AVI_JPEG", "AVI_RAW"}:
                scene.render.image_settings.file_format = target_format
            if settings.export_render_mode == "FINAL":
                bpy.ops.render.render(write_still=True, use_viewport=False)
            else:
                bpy.ops.render.opengl(write_still=True, view_context=True)
    except Exception as exc:
        print(f"Frame export failed: {exc}")
    finally:
        scene.render.filepath = prev_path
        scene.render.image_settings.file_format = prev_format
        scene.render.image_settings.color_mode = prev_color_mode

    _render_frame_idx += 1
    _total_export_frames = _render_frame_idx


def backup_vse(scene):
    """Backup VSE strips"""
    if not scene.sequence_editor:
        return None
    backup = []
    for strip in scene.sequence_editor.strips:
        backup.append({"name": strip.name})
    return backup


def restore_vse(scene, backup):
    """Remove strips added after backup"""
    if not scene.sequence_editor or backup is None:
        return
    backup_names = {b["name"] for b in backup}
    to_remove = [s.name for s in scene.sequence_editor.strips if s.name not in backup_names]
    for name in to_remove:
        strip = scene.sequence_editor.strips.get(name)
        if strip:
            scene.sequence_editor.strips.remove(strip)


def finalize_video_export(context):
    """Compose video from temp frames using VSE"""
    global _temp_frame_dir, _is_video_export, _vse_backup
    import shutil

    if not _temp_frame_dir or not os.path.isdir(_temp_frame_dir):
        return

    scene = context.scene
    settings = get_settings(context)

    
    frame_files = sorted([f for f in os.listdir(_temp_frame_dir) if f.startswith(settings.render_prefix)])
    if not frame_files:
        print("No frames to compose")
        return

    
    _vse_backup = backup_vse(scene)

    
    if not scene.sequence_editor:
        scene.sequence_editor_create()

    
    prev_frame_start = scene.frame_start
    prev_frame_end = scene.frame_end

    
    first_frame = os.path.join(_temp_frame_dir, frame_files[0])
    strip = scene.sequence_editor.strips.new_image(
        name="shaping_temp_frames",
        filepath=first_frame,
        channel=1,
        frame_start=1
    )
    
    for f in frame_files[1:]:
        strip.elements.append(f)

    
    scene.frame_start = 1
    scene.frame_end = len(frame_files)

    try:
        
        bpy.ops.render.render(animation=True)
        print(f"Video exported: {len(frame_files)} frames")
    except Exception as e:
        print(f"Video export failed: {e}")
    finally:
        
        scene.frame_start = prev_frame_start
        scene.frame_end = prev_frame_end

        
        restore_vse(scene, _vse_backup)
        _vse_backup = None

        
        try:
            shutil.rmtree(_temp_frame_dir)
        except Exception as e:
            print(f"Failed to clean temp frames: {e}")
        _temp_frame_dir = None
        _is_video_export = False


def create_mesh_from_state(state, name="playback_mesh"):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    for co in state["verts"]:
        bm.verts.new(co)
    bm.verts.ensure_lookup_table()

    for e in state["edges"]:
        if e[0] < len(bm.verts) and e[1] < len(bm.verts):
            try:
                bm.edges.new((bm.verts[e[0]], bm.verts[e[1]]))
            except ValueError:
                pass

    for f in state["faces"]:
        try:
            bm.faces.new([bm.verts[i] for i in f])
        except ValueError:
            pass

    bm.to_mesh(mesh)
    bm.free()
    return mesh


def apply_state_to_object(obj, state, name_suffix="playback"):
    new_mesh = create_mesh_from_state(state, name=f"{obj.name}_{name_suffix}")
    old_mesh = obj.data
    obj.data = new_mesh
    if old_mesh and old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)


def get_or_create_highlight_object(target_obj):
    return None


def remove_highlight_object():
    return


class MeshRecorderModal(bpy.types.Operator):
    bl_idname = "mesh.recorder_modal"
    bl_label = "Mesh Recorder Modal"
    bl_options = {"REGISTER"}

    _timer = None
    _stable_count = 0
    _pending_hash = None

    def modal(self, context, event):
        global redo_history, initial_hash, last_hash, is_recording, object_records

        if not is_recording:
            self.cancel(context)
            return {"CANCELLED"}

        if event.type == "TIMER":
            obj = context.active_object
            if obj and obj.type == "MESH" and obj.name == target_obj_name:
                rec = object_records.get(target_obj_name)
                if not rec:
                    return {"PASS_THROUGH"}
                operation_history = rec["history"]
                initial_mesh = rec["initial_mesh"]

                current_hash = get_mesh_hash(obj)
                if current_hash != last_hash:
                    if current_hash == self._pending_hash:
                        self._stable_count += 1
                        if self._stable_count >= 3:
                            base_hash = (
                                initial_hash if initial_hash is not None else last_hash
                            )
                            history_hashes = [base_hash] + [
                                s.get("hash") for s in operation_history
                            ]

                            
                            if current_hash in history_hashes:
                                match_idx = history_hashes.index(current_hash)
                                keep_len = max(0, match_idx)
                                if keep_len < len(operation_history):
                                    removed = operation_history[keep_len:]
                                    redo_history[:] = removed + redo_history
                                    del operation_history[keep_len:]
                                    print(
                                        f"Undo detected, rollback to step {keep_len}, "
                                        f"redo available: {len(redo_history)}"
                                    )
                                last_hash = current_hash

                            else:
                                
                                redo_hashes = [s.get("hash") for s in redo_history]
                                if current_hash in redo_hashes:
                                    redo_idx = redo_hashes.index(current_hash)
                                    restored = redo_history[: redo_idx + 1]
                                    operation_history.extend(restored)
                                    del redo_history[: redo_idx + 1]
                                    last_hash = current_hash
                                    print(
                                        f"Redo detected, step {len(operation_history)}, "
                                        f"redo remaining: {len(redo_history)}"
                                    )
                                else:
                                    
                                    redo_history.clear()
                                    state = save_mesh_state(obj)
                                    state["view"] = save_view_state(context)
                                    state["camera"] = save_camera_state(context)
                                    state["hash"] = current_hash
                                    operation_history.append(state)
                                    last_hash = current_hash
                                    print(
                                        f"Recorded step {len(operation_history)}, "
                                        f"verts: {len(state['verts'])}, edges: {len(state['edges'])}"
                                    )

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


def lock_other_objects(context, exclude_obj):
    """Lock all mesh objects except the one being recorded"""
    global _locked_objects
    _locked_objects = []
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj != exclude_obj and not obj.hide_select:
            obj.hide_select = True
            _locked_objects.append(obj.name)


def unlock_other_objects():
    """Unlock previously locked objects"""
    global _locked_objects
    for name in _locked_objects:
        obj = bpy.data.objects.get(name)
        if obj:
            obj.hide_select = False
    _locked_objects = []


def start_recording(context):
    global \
        is_recording, \
        initial_hash, \
        last_hash, \
        target_obj_name, \
        redo_history, \
        object_records, \
        current_display_obj

    if is_playing:
        return

    obj = context.active_object
    if not obj or obj.type != "MESH":
        return

    target_obj_name = obj.name
    current_display_obj = obj.name

    
    initial_mesh = save_mesh_state(obj)
    initial_mesh["view"] = save_view_state(context)
    initial_mesh["camera"] = save_camera_state(context)
    initial_hash = get_mesh_hash(obj)
    last_hash = initial_hash
    initial_mesh["hash"] = initial_hash

    object_records[obj.name] = {
        "initial_mesh": initial_mesh,
        "history": [],
        "redo": [],
    }
    redo_history.clear()
    is_recording = True

    
    lock_other_objects(context, obj)

    bpy.ops.mesh.recorder_modal("INVOKE_DEFAULT")
    print(f"Recording started on {obj.name}")


def stop_recording():
    global is_recording, redo_history, target_obj_name
    is_recording = False
    redo_history.clear()
    unlock_other_objects()
    rec = get_current_record()
    history_len = len(rec["history"]) if rec else 0
    sync_step_list(bpy.context)
    save_to_scene(bpy.context)
    target_obj_name = None
    print(f"Recording stopped, total steps: {history_len}")


def sync_step_list(context, keep_index=None):
    global _is_auto_selecting
    settings = get_settings(context)
    settings.step_items.clear()
    initial_mesh = get_current_initial_mesh()
    operation_history = get_current_history()
    if not initial_mesh:
        return
    item = settings.step_items.add()
    item.index = -1
    for i in range(len(operation_history)):
        item = settings.step_items.add()
        item.index = i
    _is_auto_selecting = True
    if keep_index is not None:
        settings.active_step_index = min(keep_index, len(settings.step_items) - 1)
    else:
        settings.active_step_index = 0
    _is_auto_selecting = False


def on_step_select(self, context):
    global is_playing, _jump_state
    if is_playing or is_recording or _is_auto_selecting:
        return
    if not self.step_items:
        return
    initial_mesh = get_current_initial_mesh()
    operation_history = get_current_history()
    if not initial_mesh:
        return

    target_item = self.step_items[self.active_step_index]
    target_idx = target_item.index

    
    source_idx = target_idx - 1 if target_idx > 0 else -1
    obj = get_recorded_object()

    
    edge_indices = get_edge_indices_for_step(source_idx)
    if obj:
        update_mesh_new_edge_attribute(obj, edge_indices)
    update_edge_draw_coords(source_idx)

    if target_idx == -1:
        target_state = initial_mesh
    else:
        target_state = operation_history[target_idx]
    if target_idx == -1:
        
        if obj:
            update_mesh_new_edge_attribute(obj, [])
        update_edge_draw_coords(None)
        jump_to_state_immediate(context, target_state)
        return
    source_state = initial_mesh if target_idx == 0 else operation_history[target_idx - 1]
    start_interpolated_jump(context, source_state, target_state, target_idx)


def jump_to_state_immediate(context, state):
    obj = get_recorded_object()
    if not obj:
        return
    ensure_object_mode(context, obj)
    apply_state_to_object(obj, state)
    apply_view_state(context, state.get("view"))
    apply_camera_state(context, state.get("camera"))


def start_interpolated_jump(context, source_state, target_state, step_index=0):
    global _jump_state, is_playing
    obj = get_recorded_object()
    if not obj:
        return
    ensure_object_mode(context, obj)
    settings = get_settings(context)
    apply_state_to_object(obj, source_state)
    apply_view_state(context, source_state.get("view"))
    cache = compute_step_cache(source_state, target_state)
    cam_dur, mesh_dur = get_step_timing(context, step_index)
    cam_changed = view_state_changed(source_state.get("view"), target_state.get("view"))

    
    source_step_idx = step_index - 1 if step_index > 0 else -1
    edge_indices = get_edge_indices_for_step(source_step_idx)
    update_mesh_new_edge_attribute(obj, edge_indices)
    update_edge_draw_coords(source_step_idx)

    _jump_state = {
        "source": source_state,
        "target": target_state,
        "cache": cache,
        "elapsed": 0.0,
        "cam_duration": cam_dur if cam_changed else 0.0,
        "mesh_duration": mesh_dur,
        "source_step_idx": source_step_idx,
    }
    is_playing = True
    total_dur = _jump_state["cam_duration"] + _jump_state["mesh_duration"]
    interval = total_dur / max(1, settings.interp_steps)
    bpy.app.timers.register(lambda: jump_step(context), first_interval=interval)


def jump_step(context):
    global _jump_state, is_playing
    if not is_playing or not _jump_state:
        is_playing = False
        _jump_state = None
        return None
    obj = get_recorded_object()
    if not obj:
        is_playing = False
        _jump_state = None
        return None
    settings = get_settings(context)
    cam_duration = _jump_state["cam_duration"]
    mesh_duration = _jump_state["mesh_duration"]
    total_duration = cam_duration + mesh_duration
    interval = total_duration / max(1, settings.interp_steps)
    _jump_state["elapsed"] += interval
    elapsed = _jump_state["elapsed"]
    source = _jump_state["source"]
    target = _jump_state["target"]
    cache = _jump_state["cache"]
    source_step_idx = _jump_state.get("source_step_idx", -1)

    if cam_duration > 0 and elapsed < cam_duration:
        cam_t = elapsed / cam_duration
        mesh_t = 0.0
    else:
        cam_t = 1.0
        mesh_elapsed = elapsed - cam_duration if cam_duration > 0 else elapsed
        mesh_t = min(mesh_elapsed / max(mesh_duration, 1e-6), 1.0)
    apply_view_state(context, interpolate_view_state(source.get("view"), target.get("view"), cam_t))
    apply_camera_state(context, interpolate_camera_state(source.get("camera"), target.get("camera"), cam_t))
    if mesh_t > 0:
        new_verts, topo = interpolate_states_cached(source, target, mesh_t, cache)
        if not update_mesh_vertices(obj.data, new_verts):
            apply_state_to_object(obj, {"verts": new_verts, "edges": topo["edges"], "faces": topo["faces"]})
        
        update_edge_draw_coords(source_step_idx)
    if elapsed >= total_duration:
        
        update_mesh_new_edge_attribute(obj, [])
        update_edge_draw_coords(None)
        is_playing = False
        _jump_state = None
        return None
    return interval


def get_settings(context):
    return context.scene.mesh_recorder_settings


def get_step_timing(context, step_index):
    settings = get_settings(context)
    for item in settings.step_items:
        if item.index == step_index and item.use_custom_timing:
            return item.cam_duration, item.mesh_duration
    return settings.global_cam_duration, settings.global_mesh_duration


def ensure_object_mode(context, obj):
    if obj.mode != "OBJECT":
        context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")


def play_forward(context, export_frames=False, mode="range"):
    global \
        is_playing, \
        current_step, \
        interp_progress, \
        _step_cache, \
        _render_frame_idx, \
        _playback_start_idx, \
        _playback_end_idx, \
        is_exporting_frames, \
        _temp_frame_dir, \
        _is_video_export, \
        _total_export_frames

    operation_history = get_current_history()
    initial_mesh = get_current_initial_mesh()

    if is_recording or is_playing or not operation_history:
        return

    obj = get_recorded_object()
    if not obj:
        print("No recorded target mesh")
        return

    ensure_object_mode(context, obj)

    settings = get_settings(context)
    is_exporting_frames = bool(export_frames)

    
    _is_video_export = False
    _temp_frame_dir = None
    if export_frames:
        scene = context.scene
        movie_formats = {"FFMPEG", "AVI_JPEG", "AVI_RAW"}
        if scene.render.image_settings.file_format in movie_formats:
            _is_video_export = True
            base_path = bpy.path.abspath(scene.render.filepath)
            out_dir = os.path.dirname(base_path) if base_path else bpy.path.abspath("//")
            _temp_frame_dir = os.path.join(out_dir, "_temp_frames")
            os.makedirs(_temp_frame_dir, exist_ok=True)

    if mode == "start":
        start_idx = 0
        end_idx = len(operation_history) - 1
    elif mode == "active":
        idx = settings.active_step_index
        start_idx = max(0, idx - 1) if idx > 0 else 0
        end_idx = len(operation_history) - 1
    else:  
        start_idx = max(0, min(len(operation_history) - 1, settings.playback_start_step - 1))
        end_idx = (
            settings.playback_end_step - 1
            if settings.playback_end_step > 0
            else len(operation_history) - 1
        )
        end_idx = max(start_idx, min(len(operation_history) - 1, end_idx))

    _playback_start_idx = start_idx
    _playback_end_idx = end_idx

    
    if start_idx == 0:
        apply_state_to_object(obj, initial_mesh, name_suffix="start")
        apply_view_state(context, initial_mesh.get("view"))
        apply_camera_state(context, initial_mesh.get("camera"))
    else:
        prev_state = operation_history[start_idx - 1]
        apply_state_to_object(obj, prev_state, name_suffix="start")
        apply_view_state(context, prev_state.get("view"))
        apply_camera_state(context, prev_state.get("camera"))

    current_step = start_idx
    interp_progress = 0.0
    _step_cache = None
    _render_frame_idx = 0
    is_playing = True
    lock_view_to_camera(context, True)
    toggle_overlays(True)

    interval = settings.step_duration / max(1, settings.interp_steps)
    bpy.app.timers.register(lambda: play_step(context), first_interval=interval)
    print(f"Playing forward, total steps: {len(operation_history)}")


def play_step(context):
    global current_step, is_playing, interp_progress, _step_cache, _playback_end_idx, _is_auto_selecting

    if not is_playing:
        return None

    obj = get_recorded_object()
    if not obj:
        stop_playing()
        return None

    operation_history = get_current_history()
    initial_mesh = get_current_initial_mesh()

    settings = get_settings(context)
    interp_steps = max(1, settings.interp_steps)
    interval = settings.step_duration / interp_steps

    
    _is_auto_selecting = True
    settings.active_step_index = current_step + 1  
    _is_auto_selecting = False

    if current_step > _playback_end_idx:
        stop_playing()
        return None

    target_state = operation_history[current_step]
    source_state = (
        initial_mesh if current_step == 0 else operation_history[current_step - 1]
    )

    
    source_step_idx = current_step - 1 if current_step > 0 else -1

    cache_key = current_step
    if _step_cache is None or _step_cache.get("key") != cache_key:
        _step_cache = compute_step_cache(source_state, target_state)
        _step_cache["key"] = cache_key
        
        edge_indices = get_edge_indices_for_step(source_step_idx)
        update_mesh_new_edge_attribute(obj, edge_indices)
        update_edge_draw_coords(source_step_idx)

    
    interp_progress += interval

    cam_changed = view_state_changed(
        source_state.get("view"), target_state.get("view")
    ) or camera_state_changed(source_state.get("camera"), target_state.get("camera"))

    step_cam_dur, step_mesh_dur = get_step_timing(context, current_step)
    cam_duration = step_cam_dur if cam_changed else 0.0
    mesh_duration = step_mesh_dur
    total_duration = cam_duration + mesh_duration

    elapsed = interp_progress

    if cam_changed and elapsed < cam_duration:
        cam_t = elapsed / cam_duration if cam_duration > 0.0 else 1.0
        mesh_t = 0.0
    else:
        cam_t = 1.0 if cam_changed else min(elapsed / mesh_duration, 1.0)
        mesh_elapsed = elapsed - cam_duration if cam_changed else elapsed
        mesh_t = min(mesh_elapsed / max(mesh_duration, 1e-6), 1.0)

    if elapsed >= total_duration:
        apply_view_state(context, target_state.get("view"))
        apply_camera_state(context, target_state.get("camera"))
        apply_state_to_object(obj, target_state)
        
        update_mesh_new_edge_attribute(obj, [])
        update_edge_draw_coords(None)
        maybe_render_viewport_frame(context)

        current_step += 1
        interp_progress = 0.0
        _step_cache = None
        return interval

    
    apply_view_state(
        context,
        interpolate_view_state(
            source_state.get("view"), target_state.get("view"), cam_t
        ),
    )
    apply_camera_state(
        context,
        interpolate_camera_state(
            source_state.get("camera"), target_state.get("camera"), cam_t
        ),
    )

    
    if not (cam_changed and elapsed < cam_duration):
        new_verts, topo_state = interpolate_states_cached(
            source_state, target_state, mesh_t, _step_cache
        )
        if not update_mesh_vertices(obj.data, new_verts):
            apply_state_to_object(
                obj,
                {
                    "verts": new_verts,
                    "edges": topo_state["edges"],
                    "faces": topo_state["faces"],
                },
            )
        
        update_edge_draw_coords(source_step_idx)

    maybe_render_viewport_frame(context)

    return interval


def highlight_new_edges(obj, prev_state, curr_state, mapping_prev_to_curr=None):
    """ """
    return


def stop_playing():
    global is_playing, _step_cache, interp_progress, is_exporting_frames, _total_export_frames
    was_video_export = _is_video_export
    is_playing = False
    _step_cache = None
    interp_progress = 0.0
    is_exporting_frames = False
    lock_view_to_camera(bpy.context, False)
    toggle_overlays(False)
    if was_video_export:
        finalize_video_export(bpy.context)
    _total_export_frames = 0
    print("Playing stopped")


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


class MeshRecorderStepItem(bpy.types.PropertyGroup):
    index: bpy.props.IntProperty()
    use_custom_timing: bpy.props.BoolProperty(
        name="Use Custom Timing",
        description="Use Custom Timing",
        default=False
    )
    cam_duration: bpy.props.FloatProperty(
        name="Camera Duration",
        description="Camera animation duration for this step",
        default=0.5, min=0.0, max=10.0
    )
    mesh_duration: bpy.props.FloatProperty(
        name="Mesh Duration",
        description="Mesh animation duration for this step",
        default=0.5, min=0.1, max=10.0
    )
    show_changed_edges: bpy.props.BoolProperty(default=False)
    marked_edge_indices: bpy.props.StringProperty(default="")


class MESH_UL_recorder_steps(bpy.types.UIList):
    bl_idname = "MESH_UL_recorder_steps"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        if item.index == -1:
            row.label(text=iface_("Step 0 (Initial)"))
        else:
            mark = " *" if item.use_custom_timing else ""
            row.label(text=iface_("Step {n}").format(n=item.index + 1) + mark)
            edge_icon = "HIDE_OFF" if item.show_changed_edges else "HIDE_ON"
            op = row.operator("mesh.toggle_changed_edges", text="", icon=edge_icon)
            op.step_index = item.index
            op = row.operator("mesh.delete_recorder_step", text="", icon="X")
            op.step_index = item.index


class MeshRecorderSettings(bpy.types.PropertyGroup):
    step_duration: bpy.props.FloatProperty(
        name="Step Duration",
        description="Seconds between steps",
        default=0.5,
        min=0.1,
        max=5.0,
    )
    interp_steps: bpy.props.IntProperty(
        name="Interpolation Steps",
        description="Interpolation frames per step",
        default=10,
        min=1,
        max=60,
    )
    playback_start_step: bpy.props.IntProperty(
        name="Start Step",
        description="First recorded step to replay (1-based)",
        default=1,
        min=1,
    )
    playback_end_step: bpy.props.IntProperty(
        name="End Step",
        description="Last recorded step to replay (1-based, 0 = to end)",
        default=0,
        min=0,
    )
    render_prefix: bpy.props.StringProperty(
        name="File Prefix",
        description="Frame file prefix",
        default="frame",
    )
    export_render_mode: bpy.props.EnumProperty(
        name="Export Render Mode",
        description="How to render frames when recording",
        items=[
            ("VIEWPORT", "Viewport", "Use OpenGL viewport render"),
            ("FINAL", "Final Render", "Use scene render engine"),
        ],
        default="VIEWPORT",
    )
    step_items: bpy.props.CollectionProperty(type=MeshRecorderStepItem)
    active_step_index: bpy.props.IntProperty(
        name="Active Step",
        description="Select a step from the list",
        update=on_step_select
    )
    global_cam_duration: bpy.props.FloatProperty(
        name="Camera Duration",
        description="Global camera animation duration between steps",
        default=0.5, min=0.0, max=10.0
    )
    global_mesh_duration: bpy.props.FloatProperty(
        name="Mesh Duration",
        description="Global mesh animation duration between steps",
        default=0.5, min=0.1, max=10.0
    )
    edge_color: bpy.props.FloatVectorProperty(
        name="Edge Color",
        subtype='COLOR_GAMMA',
        size=4,
        default=(1.0, 1.0, 0.0, 1.0),
        min=0.0, max=1.0
    )
    edge_width: bpy.props.FloatProperty(
        name="Edge Width",
        default=2.0, min=1.0, max=10.0
    )
    edge_glow: bpy.props.FloatProperty(
        name="Edge Glow",
        default=0.0, min=0.0, max=5.0
    )
    playback_mode: bpy.props.EnumProperty(
        name="Playback Mode",
        description="Choose playback/recording mode",
        items=[
            ("START", "From Start", "Play/record from beginning"),
            ("ACTIVE", "From Active", "Play/record from selected step"),
            ("RANGE", "From Range", "Play/record within specified range"),
        ],
        default="START",
    )
    show_edge_settings: bpy.props.BoolProperty(
        name="Show Edge Settings",
        default=False,
    )


class MeshRecorderPanel(bpy.types.Panel):
    bl_label = iface_("Shaping Recorder")
    bl_idname = "MESH_PT_recorder"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shaping Recorder"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.mesh_recorder_settings
        operation_history = get_current_history()

        
        if current_display_obj:
            layout.label(text=iface_("Object: {name}").format(name=current_display_obj), icon="OBJECT_DATA")
        else:
            layout.label(text=iface_("No recorded object"), icon="OBJECT_DATA")

        layout.label(text=iface_("Steps: {n}").format(n=len(operation_history)))

        
        if is_exporting_frames and _render_frame_idx > 0:
            layout.label(text=iface_("Exporting: {n} frames").format(n=_render_frame_idx), icon="RENDER_ANIMATION")

        row = layout.row()
        if not is_recording:
            row.operator("mesh.start_recording", text=iface_("Start Recording"))
        else:
            row.operator("mesh.stop_recording", text=iface_("Stop Recording"))

        if settings.step_items:
            layout.template_list(
                "MESH_UL_recorder_steps", "",
                settings, "step_items",
                settings, "active_step_index",
                rows=4
            )
            if _deleted_step is not None:
                layout.operator("mesh.restore_recorder_step", icon="LOOP_BACK")
            if settings.active_step_index < len(settings.step_items):
                item = settings.step_items[settings.active_step_index]
                if item.index != -1:
                    box = layout.box()
                    box.label(text=iface_("Step {n} Settings").format(n=item.index + 1))
                    row = box.row(align=True)
                    if _is_resetting_view:
                        row.label(text=iface_("Resetting..."))
                    else:
                        row.operator("mesh.reset_step_view", text=iface_("Reset Camera"))
                    row.operator("mesh.confirm_step_view", text=iface_("Confirm Camera"))
                    box.prop(item, "use_custom_timing", text=iface_("Use Custom Timing"))
                    if item.use_custom_timing:
                        box.prop(item, "cam_duration", text=iface_("Camera Duration"))
                        box.prop(item, "mesh_duration", text=iface_("Mesh Duration"))
                    row = box.row(align=True)
                    row.operator("mesh.set_start_step", text=iface_("Set Start"))
                    row.operator("mesh.set_end_step", text=iface_("Set End"))

                    
                    edge_box = box.box()
                    row = edge_box.row()
                    row.prop(settings, "show_edge_settings",
                             icon="TRIA_DOWN" if settings.show_edge_settings else "TRIA_RIGHT",
                             text=iface_("Edge Display"),
                             emboss=False)
                    if settings.show_edge_settings:
                        row = edge_box.row(align=True)
                        row.operator("mesh.mark_new_edge", text=iface_("Mark Edge"))
                        row.operator("mesh.confirm_new_edge", text=iface_("Confirm"))
                        edge_box.prop(settings, "edge_color")
                        edge_box.prop(settings, "edge_width")
                        edge_box.prop(settings, "edge_glow")

        layout.separator()
        layout.label(text=iface_("Global Settings"))
        layout.prop(settings, "global_cam_duration")
        layout.prop(settings, "global_mesh_duration")
        layout.prop(settings, "interp_steps")

        layout.separator()
        layout.label(
            text=iface_("Replay Range (1..{n})").format(n=len(operation_history))
        )
        row = layout.row(align=True)
        row.prop(settings, "playback_start_step")
        row.prop(settings, "playback_end_step")

        layout.separator()
        layout.label(text=iface_("Playback Mode"))
        layout.prop(settings, "playback_mode", expand=True)

        row = layout.row(align=True)
        row.operator("mesh.record_unified", text=iface_("Record"))
        row.operator("mesh.play_unified", text=iface_("Play"))
        layout.operator("mesh.stop_playing", text=iface_("Stop"))

        layout.separator()
        layout.label(text=iface_("Frame Export (Sequence)"))
        layout.prop(settings, "render_prefix")
        layout.prop(settings, "export_render_mode")
        layout.label(text=iface_("Uses Output Path directory from Render Properties."))


class StartRecordingOperator(bpy.types.Operator):
    bl_idname = "mesh.start_recording"
    bl_label = "Start Recording"
    bl_description = "Start recording mesh deformation steps"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH" and not is_recording and not is_playing

    def execute(self, context):
        start_recording(context)
        return {"FINISHED"}


class StopRecordingOperator(bpy.types.Operator):
    bl_idname = "mesh.stop_recording"
    bl_label = "Stop Recording"
    bl_description = "Stop the current recording session"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_recording

    def execute(self, context):
        stop_recording()
        return {"FINISHED"}


class StopPlayingOperator(bpy.types.Operator):
    bl_idname = "mesh.stop_playing"
    bl_label = "Stop Playing"
    bl_description = "Stop playback and return to initial state"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_playing

    def execute(self, context):
        stop_playing()
        return {"FINISHED"}


class DeleteStepOperator(bpy.types.Operator):
    bl_idname = "mesh.delete_recorder_step"
    bl_label = "Delete Step"
    bl_description = "Delete the selected step from the recording"
    bl_options = {"REGISTER", "UNDO"}

    step_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return not is_recording and not is_playing

    def execute(self, context):
        global _deleted_step
        idx = self.step_index
        operation_history = get_current_history()
        if idx < 0 or idx >= len(operation_history):
            return {"CANCELLED"}
        settings = get_settings(context)
        current_index = settings.active_step_index
        timing_data = None
        for item in settings.step_items:
            if item.index == idx:
                timing_data = {
                    "use_custom": item.use_custom_timing,
                    "cam": item.cam_duration,
                    "mesh": item.mesh_duration,
                }
                break
        _deleted_step = {
            "index": idx,
            "state": operation_history[idx],
            "timing": timing_data,
            "obj_name": current_display_obj,
        }
        del operation_history[idx]
        sync_step_list(context, keep_index=current_index)
        save_to_scene(context)
        return {"FINISHED"}


class RestoreStepOperator(bpy.types.Operator):
    bl_idname = "mesh.restore_recorder_step"
    bl_label = "Restore Deleted Step"
    bl_description = "Restore the most recently deleted step"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if _deleted_step is None or is_recording or is_playing:
            return False
        
        return _deleted_step.get("obj_name") == current_display_obj

    def execute(self, context):
        global _deleted_step
        idx = _deleted_step["index"]
        state = _deleted_step["state"]
        timing = _deleted_step.get("timing")
        operation_history = get_current_history()
        operation_history.insert(idx, state)
        sync_step_list(context)
        if timing:
            settings = get_settings(context)
            for item in settings.step_items:
                if item.index == idx:
                    item.use_custom_timing = timing.get("use_custom", False)
                    item.cam_duration = timing.get("cam", 0.5)
                    item.mesh_duration = timing.get("mesh", 0.5)
                    break
        _deleted_step = None
        save_to_scene(context)
        return {"FINISHED"}


class ResetStepViewOperator(bpy.types.Operator):
    bl_idname = "mesh.reset_step_view"
    bl_label = "Reset Camera"
    bl_description = "Reset the camera for this step to its recorded state"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if is_recording or is_playing or _is_resetting_view:
            return False
        settings = get_settings(context)
        if not settings.step_items:
            return False
        item = settings.step_items[settings.active_step_index]
        return item.index >= 0

    def execute(self, context):
        global _is_resetting_view
        _is_resetting_view = True
        return {"FINISHED"}


class ConfirmStepViewOperator(bpy.types.Operator):
    bl_idname = "mesh.confirm_step_view"
    bl_label = "Confirm Camera"
    bl_description = "Confirm and save the current camera for this step"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return _is_resetting_view

    def execute(self, context):
        global _is_resetting_view
        settings = get_settings(context)
        item = settings.step_items[settings.active_step_index]
        operation_history = get_current_history()
        operation_history[item.index]["view"] = save_view_state(context)
        save_to_scene(context)
        _is_resetting_view = False
        return {"FINISHED"}


class PlayFromActiveOperator(bpy.types.Operator):
    bl_idname = "mesh.play_from_active"
    bl_label = "Play"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (not is_recording) and (not is_playing) and bool(get_current_history())

    def execute(self, context):
        play_forward(context, export_frames=False, mode="active")
        return {"FINISHED"}


class PlayFromRangeOperator(bpy.types.Operator):
    bl_idname = "mesh.play_from_range"
    bl_label = "Play"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (not is_recording) and (not is_playing) and bool(get_current_history())

    def execute(self, context):
        play_forward(context, export_frames=False, mode="range")
        return {"FINISHED"}


class PlayFromStartOperator(bpy.types.Operator):
    bl_idname = "mesh.play_from_start"
    bl_label = "Play"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (not is_recording) and (not is_playing) and bool(get_current_history())

    def execute(self, context):
        play_forward(context, export_frames=False, mode="start")
        return {"FINISHED"}


class PlayUnifiedOperator(bpy.types.Operator):
    bl_idname = "mesh.play_unified"
    bl_label = "Play"
    bl_description = "Play back the recorded steps with interpolation"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (not is_recording) and (not is_playing) and bool(get_current_history())

    def execute(self, context):
        settings = get_settings(context)
        mode_map = {
            "START": "start",
            "ACTIVE": "active",
            "RANGE": "range"
        }
        mode = mode_map.get(settings.playback_mode, "range")
        play_forward(context, export_frames=False, mode=mode)
        return {"FINISHED"}


class RecordFromActiveOperator(bpy.types.Operator):
    bl_idname = "mesh.record_from_active"
    bl_label = "Record"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (not is_recording) and (not is_playing) and bool(get_current_history())

    def execute(self, context):
        play_forward(context, export_frames=True, mode="active")
        return {"FINISHED"}


class RecordFromRangeOperator(bpy.types.Operator):
    bl_idname = "mesh.record_from_range"
    bl_label = "Record"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (not is_recording) and (not is_playing) and bool(get_current_history())

    def execute(self, context):
        play_forward(context, export_frames=True, mode="range")
        return {"FINISHED"}


class RecordFromStartOperator(bpy.types.Operator):
    bl_idname = "mesh.record_from_start"
    bl_label = "Record"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (not is_recording) and (not is_playing) and bool(get_current_history())

    def execute(self, context):
        play_forward(context, export_frames=True, mode="start")
        return {"FINISHED"}


class RecordUnifiedOperator(bpy.types.Operator):
    bl_idname = "mesh.record_unified"
    bl_label = "Record"
    bl_description = "Record frames of the playback for export"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (not is_recording) and (not is_playing) and bool(get_current_history())

    def execute(self, context):
        settings = get_settings(context)
        mode_map = {
            "START": "start",
            "ACTIVE": "active",
            "RANGE": "range"
        }
        mode = mode_map.get(settings.playback_mode, "range")
        play_forward(context, export_frames=True, mode=mode)
        return {"FINISHED"}


class SetStartStepOperator(bpy.types.Operator):
    bl_idname = "mesh.set_start_step"
    bl_label = "Set Start"
    bl_description = "Set the current step as the playback start point"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if is_recording or is_playing:
            return False
        settings = get_settings(context)
        if not settings.step_items:
            return False
        item = settings.step_items[settings.active_step_index]
        return item.index >= 0

    def execute(self, context):
        settings = get_settings(context)
        item = settings.step_items[settings.active_step_index]
        new_start = item.index + 1
        if settings.playback_end_step == 0 or new_start <= settings.playback_end_step:
            settings.playback_start_step = new_start
        return {"FINISHED"}


class SetEndStepOperator(bpy.types.Operator):
    bl_idname = "mesh.set_end_step"
    bl_label = "Set End"
    bl_description = "Set the current step as the playback end point"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if is_recording or is_playing:
            return False
        settings = get_settings(context)
        if not settings.step_items:
            return False
        item = settings.step_items[settings.active_step_index]
        return item.index >= 0

    def execute(self, context):
        settings = get_settings(context)
        item = settings.step_items[settings.active_step_index]
        new_end = item.index + 1
        if new_end >= settings.playback_start_step:
            settings.playback_end_step = new_end
        return {"FINISHED"}


class ToggleChangedEdgesOperator(bpy.types.Operator):
    bl_idname = "mesh.toggle_changed_edges"
    bl_label = "Toggle Highlighted Edges"
    bl_description = "Toggle display of highlighted edges for this step"
    bl_options = {"REGISTER", "UNDO"}

    step_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return not is_recording and not is_playing and current_display_obj

    def execute(self, context):
        settings = get_settings(context)
        item = None
        for it in settings.step_items:
            if it.index == self.step_index:
                item = it
                break
        if not item:
            return {"CANCELLED"}

        item.show_changed_edges = not item.show_changed_edges
        obj = get_recorded_object()

        
        settings = get_settings(context)
        target_idx = settings.step_items[settings.active_step_index].index if settings.step_items else -1
        source_idx = target_idx - 1 if target_idx > 0 else -1

        edge_indices = get_edge_indices_for_step(source_idx)
        if obj:
            update_mesh_new_edge_attribute(obj, edge_indices)
        update_edge_draw_coords(source_idx)
        return {"FINISHED"}


class MarkEdgeOperator(bpy.types.Operator):
    bl_idname = "mesh.mark_new_edge"
    bl_label = "Mark Edge"
    bl_description = "Enter edge marking mode to select edges to highlight"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if is_recording or is_playing or _is_marking_edge:
            return False
        if not current_display_obj:
            return False
        settings = get_settings(context)
        if not settings.step_items:
            return False
        if settings.active_step_index < 0 or settings.active_step_index >= len(settings.step_items):
            return False
        item = settings.step_items[settings.active_step_index]
        return item.index >= 0

    def execute(self, context):
        global _is_marking_edge, _marking_step_index
        settings = get_settings(context)
        if settings.active_step_index >= len(settings.step_items):
            return {"CANCELLED"}
        item = settings.step_items[settings.active_step_index]
        _marking_step_index = item.index
        _is_marking_edge = True

        obj = get_recorded_object()
        if obj:
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='EDGE')
            bpy.ops.mesh.select_all(action='DESELECT')
        return {"FINISHED"}


class ConfirmEdgeOperator(bpy.types.Operator):
    bl_idname = "mesh.confirm_new_edge"
    bl_label = "Confirm"
    bl_description = "Confirm the selected edges and save for this step"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return _is_marking_edge

    def execute(self, context):
        global _is_marking_edge, _marking_step_index

        obj = get_recorded_object()
        if not obj or obj.mode != 'EDIT':
            _is_marking_edge = False
            _marking_step_index = -1
            return {"CANCELLED"}

        
        bm = bmesh.from_edit_mesh(obj.data)
        edge_indices = [[e.verts[0].index, e.verts[1].index] for e in bm.edges if e.select]

        bpy.ops.object.mode_set(mode='OBJECT')

        settings = get_settings(context)
        for item in settings.step_items:
            if item.index == _marking_step_index:
                item.marked_edge_indices = json.dumps(edge_indices)
                item.show_changed_edges = True
                break

        
        target_idx = settings.step_items[settings.active_step_index].index if settings.step_items else -1
        source_idx = target_idx - 1 if target_idx > 0 else -1
        display_edges = get_edge_indices_for_step(source_idx)
        update_mesh_new_edge_attribute(obj, display_edges)
        update_edge_draw_coords(source_idx)
        save_to_scene(context)

        _is_marking_edge = False
        _marking_step_index = -1
        return {"FINISHED"}


classes = (
    MeshRecorderStepItem,
    MESH_UL_recorder_steps,
    MeshRecorderSettings,
    MeshRecorderModal,
    MeshRecorderPanel,
    StartRecordingOperator,
    StopRecordingOperator,
    StopPlayingOperator,
    DeleteStepOperator,
    RestoreStepOperator,
    ResetStepViewOperator,
    ConfirmStepViewOperator,
    PlayFromActiveOperator,
    PlayFromRangeOperator,
    PlayFromStartOperator,
    RecordFromActiveOperator,
    RecordFromRangeOperator,
    RecordFromStartOperator,
    RecordUnifiedOperator,
    PlayUnifiedOperator,
    SetStartStepOperator,
    SetEndStepOperator,
    ToggleChangedEdgesOperator,
    MarkEdgeOperator,
    ConfirmEdgeOperator,
)


def register():
    global _edge_draw_handler
    bpy.app.translations.register(__name__, translations)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mesh_recorder_settings = bpy.props.PointerProperty(
        type=MeshRecorderSettings
    )
    if load_post_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_post_handler)
    if depsgraph_update_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_handler)
    _edge_draw_handler = bpy.types.SpaceView3D.draw_handler_add(
        draw_changed_edges, (), 'WINDOW', 'POST_VIEW')


def unregister():
    global _edge_draw_handler
    stop_playing()
    unlock_other_objects()
    if _edge_draw_handler:
        bpy.types.SpaceView3D.draw_handler_remove(_edge_draw_handler, 'WINDOW')
        _edge_draw_handler = None
    if depsgraph_update_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_handler)
    if load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post_handler)
    if hasattr(bpy.types.Scene, "mesh_recorder_settings"):
        del bpy.types.Scene.mesh_recorder_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.app.translations.unregister(__name__)
