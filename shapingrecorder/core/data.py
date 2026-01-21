# Data serialization and deserialization functions for ShapingRecorder

def serialize_view(view):
    """Serialize view state for storage"""
    if not view:
        return None
    return {
        "view_perspective": view.get("view_perspective"),
        "view_location": list(view["view_location"]),
        "view_rotation": list(view["view_rotation"]),
        "view_distance": view.get("view_distance"),
    }


def deserialize_view(data):
    """Deserialize view state from storage"""
    if not data:
        return None
    from mathutils import Vector, Quaternion
    return {
        "view_perspective": data.get("view_perspective"),
        "view_location": Vector(data["view_location"]),
        "view_rotation": Quaternion(data["view_rotation"]),
        "view_distance": data.get("view_distance"),
    }


def serialize_camera(cam):
    """Serialize camera state for storage"""
    if not cam:
        return None
    return {
        "location": list(cam["location"]),
        "rotation": list(cam["rotation"]),
    }


def deserialize_camera(data):
    """Deserialize camera state from storage"""
    if not data:
        return None
    from mathutils import Vector, Quaternion
    return {
        "location": Vector(data["location"]),
        "rotation": Quaternion(data["rotation"]),
    }


def serialize_state(state):
    """Serialize mesh state for storage"""
    if not state:
        return None
    return {
        "verts": [[v.x, v.y, v.z] for v in state["verts"]],
        "edges": state["edges"],
        "faces": state["faces"],
        "hash": state.get("hash"),
        "view": serialize_view(state.get("view")),
        "camera": serialize_camera(state.get("camera")),
    }


def deserialize_state(data):
    """Deserialize mesh state from storage"""
    if not data:
        return None
    from mathutils import Vector
    return {
        "verts": [Vector(v) for v in data["verts"]],
        "edges": [tuple(e) for e in data["edges"]],
        "faces": [tuple(f) for f in data["faces"]],
        "hash": data.get("hash"),
        "view": deserialize_view(data.get("view")),
        "camera": deserialize_camera(data.get("camera")),
    }