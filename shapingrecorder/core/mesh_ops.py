# Mesh operations and utilities for ShapingRecorder

import bmesh
from array import array
from mathutils import kdtree, Vector
from mathutils.bvhtree import BVHTree

def get_mesh_hash(obj):
    """Calculate hash of mesh geometry for change detection"""
    # 如果传入的是 Evaluated Object，直接读取 data
    mesh = obj.data

    if obj.mode == "EDIT":
        bm = bmesh.from_edit_mesh(mesh)
        verts = tuple(
            (round(v.co.x, 4), round(v.co.y, 4), round(v.co.z, 4)) for v in bm.verts
        )
        edges = len(bm.edges)
    else:
        # Object/Sculpt 模式下直接读取 mesh 数据块
        # 对于 Dyntopo，必须确保传入的是 evaluated_obj
        coords = [0.0] * (len(mesh.vertices) * 3)
        mesh.vertices.foreach_get("co", coords)
        verts = tuple(round(c, 4) for c in coords)
        edges = len(mesh.edges)
    return hash((verts, edges))


def save_mesh_state(obj):
    """Save current mesh state (vertices, edges, faces)"""
    mesh = obj.data

    if obj.mode == "EDIT":
        bm = bmesh.from_edit_mesh(mesh)
        verts = [v.co.copy() for v in bm.verts]
        edges = [(e.verts[0].index, e.verts[1].index) for e in bm.edges]
        faces = [tuple(v.index for v in f.verts) for f in bm.faces]
    else:
        verts = [v.co.copy() for v in mesh.vertices]
        edges = [(e.vertices[0], e.vertices[1]) for e in mesh.edges]
        faces = [tuple(f.vertices) for f in mesh.polygons]
    return {"verts": verts, "edges": edges, "faces": faces}


def update_mesh_vertices(mesh, verts):
    """Update mesh vertices with new positions"""
    if len(mesh.vertices) != len(verts):
        return False
    coords = array("f", (c for v in verts for c in v))
    mesh.vertices.foreach_set("co", coords)
    mesh.update()
    return True


def compute_step_cache(source_state, target_state):
    """
    Compute interpolation using a Prioritized Hybrid Strategy.

    Logic Flow:
    1. Is the point VERY CLOSE to an old vertex?
       -> YES: It's a Bevel/Chamfer/Grow. Snap to Vertex (Animation: Grow).
    2. Is the point ON the old surface?
       -> YES: It's a Loop Cut/Subdivision. Snap to Surface (Animation: Static/Fade).
    3. Is the point OFF the surface?
       -> YES: It's an Extrusion. Snap to Nearest Vertex (Animation: Grow/Extrude).
    """
    verts1 = source_state["verts"]
    verts2 = target_state["verts"]
    n1 = len(verts1)
    n2 = len(verts2)

    # 1. Topology Check
    def _topo_signature(state):
        edges = state.get("edges") or []
        faces = state.get("faces") or []
        return len(edges), len(faces)

    topo_same = False
    if n1 == n2:
        try:
            e_count1, f_count1 = _topo_signature(source_state)
            e_count2, f_count2 = _topo_signature(target_state)
            if e_count1 == e_count2 and f_count1 == f_count2:
                topo_same = True
        except Exception:
            topo_same = False

    if topo_same:
        return {
            "n1": n1,
            "n2": n2,
            "mode": "direct",
        }

    # 2. Setup Spatial Search
    # Calculate scale for adaptive thresholds
    if n1 > 0:
        min_v = Vector((float('inf'), float('inf'), float('inf')))
        max_v = Vector((float('-inf'), float('-inf'), float('-inf')))
        for v in verts1:
            min_v.x = min(min_v.x, v.x)
            min_v.y = min(min_v.y, v.y)
            min_v.z = min(min_v.z, v.z)
            max_v.x = max(max_v.x, v.x)
            max_v.y = max(max_v.y, v.y)
            max_v.z = max(max_v.z, v.z)
        bbox_diag = (max_v - min_v).length
    else:
        bbox_diag = 1.0

    # Thresholds
    # SNAP_THRESHOLD: Within this distance, we assume the point originated from the vertex.
    # 15% is generous enough to catch large bevels but small enough to miss mid-edge loop cuts.
    SNAP_THRESHOLD = max(0.02, bbox_diag * 0.15)

    # SURFACE_EPSILON: Tolerance to consider a point "On the Surface".
    SURFACE_EPSILON = 1e-4

    # Build BVH (Source Surface)
    bm_temp = bmesh.new()
    source_bm_verts = []
    for co in verts1:
        source_bm_verts.append(bm_temp.verts.new(co))
    bm_temp.verts.ensure_lookup_table()
    for e in source_state.get("edges", []):
        try: bm_temp.edges.new((source_bm_verts[e[0]], source_bm_verts[e[1]]))
        except ValueError: pass
    for f in source_state.get("faces", []):
        try: bm_temp.faces.new([source_bm_verts[i] for i in f])
        except ValueError: pass
    if bm_temp.faces:
        bmesh.ops.triangulate(bm_temp, faces=bm_temp.faces)

    try:
        bvh = BVHTree.FromBMesh(bm_temp)
    except:
        bvh = None

    # Build KDTree (Source Vertices)
    kd = kdtree.KDTree(n1)
    for i, v in enumerate(verts1):
        kd.insert(v, i)
    kd.balance()

    source_locations = []

    for v2 in verts2:
        start_loc = v2 # Fallback

        # Get Surface Point (Projection)
        loc_surf = None
        dist_surf = 99999.0
        if bvh:
            loc_surf, _, _, dist_surf = bvh.find_nearest(v2)

        # Get Vertex Point (Snap)
        loc_vert, _, dist_vert = kd.find(v2)

        # --- PRIORITY LOGIC ---

        # Priority 1: Closeness to Vertex (Handles Bevels, Chamfers)
        # If we are close to an old vertex, we almost certainly grew from it.
        # This fixes "Vertex Bevel shrinking" by forcing it to snap to the corner.
        if dist_vert < SNAP_THRESHOLD:
            start_loc = loc_vert

        # Priority 2: On Surface (Handles Loop Cuts, Subdivisions)
        # If we aren't close to a vertex, but we are ON the surface, stay there.
        elif bvh and loc_surf and dist_surf < SURFACE_EPSILON:
            start_loc = loc_surf

        # Priority 3: Off Surface (Handles Extrusions, Inflation)
        # If we are far from vertices AND far from surface, we assume extrusion.
        # Extrusion should grow from the base (nearest vertex), not project to surface.
        else:
            start_loc = loc_vert

        source_locations.append(start_loc)

    bm_temp.free()

    return {
        "n1": n1,
        "n2": n2,
        "mode": "hybrid",
        "sources": source_locations
    }


def interpolate_states_cached(source_state, target_state, t, cache):
    """Interpolate using the computed cache"""
    verts1 = source_state["verts"]
    verts2 = target_state["verts"]

    if cache.get("mode") == "direct":
        n1 = cache["n1"]
        new_verts = [verts1[i].lerp(verts2[i], t) for i in range(n1)]
        return new_verts, target_state

    if cache.get("mode") == "hybrid":
        source_locs = cache["sources"]
        new_verts = [s.lerp(e, t) for s, e in zip(source_locs, verts2)]
        return new_verts, target_state

    return [v.copy() for v in verts2], target_state
