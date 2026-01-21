import bpy


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


def get_current_record():
    if not current_display_obj or current_display_obj not in object_records:
        return None
    return object_records[current_display_obj]

def get_current_history():
    rec = get_current_record()
    return rec["history"] if rec else []

def get_current_initial_mesh():
    rec = get_current_record()
    return rec["initial_mesh"] if rec else None

def get_recorded_object():
    if not current_display_obj:
        return None
    obj = bpy.data.objects.get(current_display_obj)
    if obj and obj.type == "MESH":
        return obj
    return None

def get_settings(context):
    return context.scene.mesh_recorder_settings
