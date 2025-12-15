import bpy
from bpy.app.translations import pgettext_iface as iface_
from . import state

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

class MeshRecorderPanel(bpy.types.Panel):
    bl_label = iface_("Shaping Recorder")
    bl_idname = "MESH_PT_recorder"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shaping Recorder"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.mesh_recorder_settings
        operation_history = state.get_current_history()

        if state.current_display_obj:
            layout.label(text=iface_("Object: {name}").format(name=state.current_display_obj), icon="OBJECT_DATA")
        else:
            layout.label(text=iface_("No recorded object"), icon="OBJECT_DATA")

        layout.label(text=iface_("Steps: {n}").format(n=len(operation_history)))

        if state.is_exporting_frames and state._render_frame_idx > 0:
            layout.label(text=iface_("Exporting: {n} frames").format(n=state._render_frame_idx), icon="RENDER_ANIMATION")

        row = layout.row()
        if not state.is_recording:
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
            if state._deleted_step is not None:
                layout.operator("mesh.restore_recorder_step", icon="LOOP_BACK")
            if settings.active_step_index < len(settings.step_items):
                item = settings.step_items[settings.active_step_index]
                if item.index != -1:
                    box = layout.box()
                    box.label(text=iface_("Step {n} Settings").format(n=item.index + 1))
                    row = box.row(align=True)
                    if state._is_resetting_view:
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
                             text=iface_("Edge Display"), emboss=False)
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
        layout.label(text=iface_("Replay Range (1..{n})").format(n=len(operation_history)))
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
