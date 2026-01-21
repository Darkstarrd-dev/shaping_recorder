bl_info = {
    "name": "Shaping Recorder",
    "author": "Darkstarrd",
    "version": (0, 3, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Shaping Recorder",
    "description": (
        "Record mesh shaping steps and viewport view changes, then replay "
        "with interpolated geometry and view. Optional frame export."
    ),
    "category": "Mesh",
    "support": "COMMUNITY",
    "doc_url": "https://github.com/Darkstarrd-dev/shape_recorder",
    "tracker_url": "https://github.com/Darkstarrd-dev/shape_recorder/issues",
}

import bpy
import sys
import traceback


try:
    from . import translations
    from . import state
    from . import properties
    from . import ui
    from . import operators
    from . import handlers
    from . import graphics
except ImportError as e:
    print(f"\n[ShapingRecorder] IMPORT ERROR: {e}")
    print(traceback.format_exc())
    
    raise e

classes = (
    properties.MeshRecorderStepItem,
    ui.MESH_UL_recorder_steps,
    properties.MeshRecorderSettings,
    operators.MeshRecorderModal,
    ui.MeshRecorderPanel,
    operators.StartRecordingOperator,
    operators.StopRecordingOperator,
    operators.StopPlayingOperator,
    operators.DeleteStepOperator,
    operators.RestoreStepOperator,
    operators.ResetStepViewOperator,
    operators.ConfirmStepViewOperator,
    operators.PlayUnifiedOperator,
    operators.RecordUnifiedOperator,
    operators.SetStartStepOperator,
    operators.SetEndStepOperator,
    operators.ToggleChangedEdgesOperator,
    operators.MarkEdgeOperator,
    operators.ConfirmEdgeOperator,
    
    operators.PlayFromActiveOperator,
    operators.PlayFromRangeOperator,
    operators.PlayFromStartOperator,
    operators.RecordFromActiveOperator,
    operators.RecordFromRangeOperator,
    operators.RecordFromStartOperator,
)

def register():
    
    trans_dict = getattr(translations, "translations", {})
    bpy.app.translations.register(__name__, trans_dict)

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.mesh_recorder_settings = bpy.props.PointerProperty(
        type=properties.MeshRecorderSettings
    )

    if operators.load_post_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(operators.load_post_handler)
    if operators.depsgraph_update_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(operators.depsgraph_update_handler)

    
    state._edge_draw_handler = bpy.types.SpaceView3D.draw_handler_add(
        graphics.draw_changed_edges, (), 'WINDOW', 'POST_VIEW')

def unregister():
    operators.stop_playing()
    operators.unlock_other_objects()

    if state._edge_draw_handler:
        bpy.types.SpaceView3D.draw_handler_remove(state._edge_draw_handler, 'WINDOW')
        state._edge_draw_handler = None

    if operators.depsgraph_update_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(operators.depsgraph_update_handler)
    if operators.load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(operators.load_post_handler)

    if hasattr(bpy.types.Scene, "mesh_recorder_settings"):
        del bpy.types.Scene.mesh_recorder_settings

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.app.translations.unregister(__name__)
