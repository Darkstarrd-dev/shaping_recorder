# AGENTS.md

## Build/Test
- Blender extension (add-on) for Blender 4.2+
- No build step; install via Blender Preferences > Add-ons or Extensions
- Test manually in Blender: Edit > Preferences > Add-ons > Install from Disk
- Reload addon: `bpy.ops.preferences.addon_disable(module="ShapingRecorder")` then re-enable

## Code Style
- Python 3.10+ (Blender 4.2 requirement)
- Imports: stdlib first, then `bpy`, `bmesh`, `mathutils` from Blender
- Naming: `snake_case` for functions/variables, `PascalCase` for classes
- Blender classes: use `bl_idname`, `bl_label`, `bl_options` conventions
- Operators inherit from `bpy.types.Operator`, panels from `bpy.types.Panel`
- 4-space indentation, no type hints
- Keep changes minimal and focused; follow existing patterns
- Global state at module level for recording/playback state
- Register classes in `register()`, unregister in reverse order in `unregister()`
- Translations dict for i18n support (zh_HANS, ja_JP, es, de_DE, fr_FR, etc.)
