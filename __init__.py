bl_info = {
    "name": "Shaping Recorder",
    "author": "Darkstarrd",
    "version": (0, 3, 2),
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

from . import recorder


def register():
    recorder.register()


def unregister():
    recorder.unregister()
