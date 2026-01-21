import bpy
from ..data import state

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
        if abs(float(state1.get("view_distance", 0.0)) - float(state2.get("view_distance", 0.0))) > dist_eps:
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

def apply_view_state(context, state_data):
    if not state_data:
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
            r3d.view_perspective = state_data.get("view_perspective", r3d.view_perspective)
            r3d.view_location = state_data["view_location"]
            r3d.view_rotation = state_data["view_rotation"]
            r3d.view_distance = state_data.get("view_distance", r3d.view_distance)

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

def apply_camera_state(context, state_data):
    cam = context.scene.camera
    if not cam or not state_data:
        return
    cam.location = state_data["location"]
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = state_data["rotation"]

def lock_view_to_camera(context, lock):
    screen = context.screen or bpy.context.screen
    if not screen:
        return

    if lock:
        state._view_lock_state.clear()
        for area in screen.areas:
            if area.type == "VIEW_3D":
                space = area.spaces.active
                r3d = space.region_3d
                if not r3d:
                    continue
                state._view_lock_state[area.as_pointer()] = {
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
            s = state._view_lock_state.get(area.as_pointer())
            if not s:
                continue
            r3d.view_perspective = s["view_perspective"]
            r3d.view_location = s["view_location"]
            r3d.view_rotation = s["view_rotation"]
            r3d.view_distance = s.get("view_distance", r3d.view_distance)
    state._view_lock_state.clear()
