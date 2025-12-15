import bpy
import json
import gpu
from gpu_extras.batch import batch_for_shader
from . import state

def update_mesh_new_edge_attribute(obj, edge_indices):
    """Update new_edge attribute on main mesh."""
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
    """Update coordinates for GPU drawing based on specified step."""
    state._current_edge_coords = []

    if step_index is None or step_index < 0:
        return

    if not state.current_display_obj:
        return

    settings = state.get_settings(bpy.context)
    if not settings.step_items:
        return

    item = None
    for it in settings.step_items:
        if it.index == step_index:
            item = it
            break

    if not item or not item.show_changed_edges or not item.marked_edge_indices:
        return

    obj = state.get_recorded_object()
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
            state._current_edge_coords.extend([v0, v1])

def get_edge_indices_for_step(step_index):
    """Get marked edge indices for a specific step."""
    if step_index < 0:
        return []
    settings = state.get_settings(bpy.context)
    for item in settings.step_items:
        if item.index == step_index and item.show_changed_edges and item.marked_edge_indices:
            try:
                return json.loads(item.marked_edge_indices)
            except:
                pass
    return []

def draw_changed_edges():
    """GPU draw handler."""
    if not state._current_edge_coords:
        return

    settings = state.get_settings(bpy.context)
    color = tuple(settings.edge_color)
    width = settings.edge_width
    glow = settings.edge_glow

    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": state._current_edge_coords})

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
