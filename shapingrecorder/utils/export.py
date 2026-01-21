import bpy
import os
from ..data import state

def maybe_render_viewport_frame(context):
    if not state.is_exporting_frames:
        return

    settings = state.get_settings(context)
    scene = context.scene

    
    if state._is_video_export and state._temp_frame_dir:
        out_dir = state._temp_frame_dir
    else:
        base_path = bpy.path.abspath(scene.render.filepath)
        out_dir = os.path.dirname(base_path) if base_path else bpy.path.abspath("//")
    os.makedirs(out_dir, exist_ok=True)

    def _ext_from_format(fmt):
        mapping = {
            "PNG": ".png", "JPEG": ".jpg", "JPEG2000": ".jp2",
            "OPEN_EXR": ".exr", "OPEN_EXR_MULTILAYER": ".exr",
            "TIFF": ".tif", "TARGA": ".tga", "TARGA_RAW": ".tga",
            "BMP": ".bmp", "WEBP": ".webp", "HDR": ".hdr",
            "DPX": ".dpx", "CINEON": ".cin", "IRIS": ".rgb",
        }
        return mapping.get(fmt, ".png")

    prev_path = scene.render.filepath
    prev_format = scene.render.image_settings.file_format
    prev_color_mode = scene.render.image_settings.color_mode

    target_format = "PNG" if state._is_video_export else prev_format
    movie_formats = {"FFMPEG", "AVI_JPEG", "AVI_RAW"}
    if target_format in movie_formats:
        target_format = "PNG"

    ext = _ext_from_format(target_format)
    filepath = os.path.join(
        out_dir, f"{settings.render_prefix}_{state._render_frame_idx:04d}{ext}"
    )

    try:
        if state._is_video_export:
            
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

    state._render_frame_idx += 1
    state._total_export_frames = state._render_frame_idx

def backup_vse(scene):
    if not scene.sequence_editor:
        return None
    backup = []
    for strip in scene.sequence_editor.strips:
        backup.append({"name": strip.name})
    return backup

def restore_vse(scene, backup):
    if not scene.sequence_editor or backup is None:
        return
    backup_names = {b["name"] for b in backup}
    to_remove = [s.name for s in scene.sequence_editor.strips if s.name not in backup_names]
    for name in to_remove:
        strip = scene.sequence_editor.strips.get(name)
        if strip:
            scene.sequence_editor.strips.remove(strip)

def finalize_video_export(context):
    import shutil
    if not state._temp_frame_dir or not os.path.isdir(state._temp_frame_dir):
        return

    scene = context.scene
    settings = state.get_settings(context)

    frame_files = sorted([f for f in os.listdir(state._temp_frame_dir) if f.startswith(settings.render_prefix)])
    if not frame_files:
        return

    state._vse_backup = backup_vse(scene)
    if not scene.sequence_editor:
        scene.sequence_editor_create()

    prev_frame_start = scene.frame_start
    prev_frame_end = scene.frame_end

    first_frame = os.path.join(state._temp_frame_dir, frame_files[0])
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
    except Exception as e:
        print(f"Video export failed: {e}")
    finally:
        scene.frame_start = prev_frame_start
        scene.frame_end = prev_frame_end
        restore_vse(scene, state._vse_backup)
        state._vse_backup = None
        try:
            shutil.rmtree(state._temp_frame_dir)
        except Exception as e:
            print(f"Failed to clean temp frames: {e}")
        state._temp_frame_dir = None
        state._is_video_export = False
