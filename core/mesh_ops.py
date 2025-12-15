import bmesh
from array import array
from mathutils import kdtree, Vector
from mathutils.bvhtree import BVHTree

def get_mesh_hash(obj):
    """Calculate hash of mesh geometry for change detection"""

    mesh = obj.data

    if obj.mode == "EDIT":
        bm = bmesh.from_edit_mesh(mesh)
        verts = tuple(
            (round(v.co.x, 4), round(v.co.y, 4), round(v.co.z, 4)) for v in bm.verts
        )
        edges = len(bm.edges)
    else:

        coords = [0.0] * (len(mesh.vertices) * 3)
        mesh.vertices.foreach_get("co", coords)
        verts = tuple(round(c, 4) for c in coords)
        edges = len(mesh.edges)
    return hash((verts, edges))


def save_mesh_state(obj):

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

    if len(mesh.vertices) != len(verts):
        return False
    coords = array("f", (c for v in verts for c in v))
    mesh.vertices.foreach_set("co", coords)
    mesh.update()
    return True


def compute_step_cache(source_state, target_state):

    verts1 = source_state["verts"]
    verts2 = target_state["verts"]
    n1 = len(verts1)
    n2 = len(verts2)

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

    SNAP_THRESHOLD = max(0.02, bbox_diag * 0.15)

    SURFACE_EPSILON = 1e-4

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

    kd = kdtree.KDTree(n1)
    for i, v in enumerate(verts1):
        kd.insert(v, i)
    kd.balance()

    source_locations = []

    for v2 in verts2:
        start_loc = v2

        loc_surf = None
        dist_surf = 99999.0
        if bvh:
            loc_surf, _, _, dist_surf = bvh.find_nearest(v2)


        loc_vert, _, dist_vert = kd.find(v2)

        if dist_vert < SNAP_THRESHOLD:
            start_loc = loc_vert
        elif bvh and loc_surf and dist_surf < SURFACE_EPSILON:
            start_loc = loc_surf
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
