import bpy
import json
from . import state

def on_step_select(self, context):
    
    from . import graphics
    from . import operators

    if state.is_playing or state.is_recording or state._is_auto_selecting:
        return
    if not self.step_items:
        return
    initial_mesh = state.get_current_initial_mesh()
    operation_history = state.get_current_history()
    if not initial_mesh:
        return

    target_item = self.step_items[self.active_step_index]
    target_idx = target_item.index

    
    source_idx = target_idx
    obj = state.get_recorded_object()

    edge_indices = graphics.get_edge_indices_for_step(source_idx)
    if obj:
        graphics.update_mesh_new_edge_attribute(obj, edge_indices)
    graphics.update_edge_draw_coords(source_idx)

    if target_idx == -1:
        target_state = initial_mesh
    else:
        target_state = operation_history[target_idx]

    if target_idx == -1:
        if obj:
            graphics.update_mesh_new_edge_attribute(obj, [])
        graphics.update_edge_draw_coords(None)
        operators.jump_to_state_immediate(context, target_state)
        return

    source_state = initial_mesh if target_idx == 0 else operation_history[target_idx - 1]
    operators.start_interpolated_jump(context, source_state, target_state, target_idx)

class MeshRecorderStepItem(bpy.types.PropertyGroup):
    index: bpy.props.IntProperty()
    use_custom_timing: bpy.props.BoolProperty(
        name="Use Custom Timing", default=False
    )
    cam_duration: bpy.props.FloatProperty(
        name="Camera Duration", default=0.5, min=0.0, max=10.0
    )
    mesh_duration: bpy.props.FloatProperty(
        name="Mesh Duration", default=0.5, min=0.1, max=10.0
    )
    show_changed_edges: bpy.props.BoolProperty(default=False)
    marked_edge_indices: bpy.props.StringProperty(default="")

class MeshRecorderSettings(bpy.types.PropertyGroup):
    step_duration: bpy.props.FloatProperty(
        name="Step Duration", default=0.5, min=0.1, max=5.0
    )
    interp_steps: bpy.props.IntProperty(
        name="Interpolation Steps", default=10, min=1, max=60
    )
    playback_start_step: bpy.props.IntProperty(
        name="Start Step", default=1, min=1
    )
    playback_end_step: bpy.props.IntProperty(
        name="End Step", default=0, min=0
    )
    render_prefix: bpy.props.StringProperty(
        name="File Prefix", default="frame"
    )
    export_render_mode: bpy.props.EnumProperty(
        name="Export Render Mode",
        items=[
            ("VIEWPORT", "Viewport", "Use OpenGL viewport render"),
            ("FINAL", "Final Render", "Use scene render engine"),
        ],
        default="VIEWPORT",
    )
    step_items: bpy.props.CollectionProperty(type=MeshRecorderStepItem)
    active_step_index: bpy.props.IntProperty(
        name="Active Step", update=on_step_select
    )
    global_cam_duration: bpy.props.FloatProperty(
        name="Camera Duration", default=0.5, min=0.0, max=10.0
    )
    global_mesh_duration: bpy.props.FloatProperty(
        name="Mesh Duration", default=0.5, min=0.1, max=10.0
    )
    edge_color: bpy.props.FloatVectorProperty(
        name="Edge Color", subtype='COLOR_GAMMA', size=4,
        default=(1.0, 1.0, 0.0, 1.0), min=0.0, max=1.0
    )
    edge_width: bpy.props.FloatProperty(name="Edge Width", default=2.0, min=1.0, max=10.0)
    edge_glow: bpy.props.FloatProperty(name="Edge Glow", default=0.0, min=0.0, max=5.0)
    playback_mode: bpy.props.EnumProperty(
        name="Playback Mode",
        items=[
            ("START", "From Start", "Play/record from beginning"),
            ("ACTIVE", "From Active", "Play/record from selected step"),
            ("RANGE", "From Range", "Play/record within specified range"),
        ],
        default="START",
    )
    show_edge_settings: bpy.props.BoolProperty(name="Show Edge Settings", default=False)
