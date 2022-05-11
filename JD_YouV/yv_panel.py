import bpy

from bpy.types import Panel

# --- PARENT CLASSES, don't register
class YV_PT_VIEW_3D:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "YouV"

class YV_PT_IMAGE_EDITOR:
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_category = "YouV"


# ----- 3D VIEWPORT PANELS

# ----- UV EDITOR PANELS

# -- DEV PANELS
class YV_PT_DEV(YV_PT_IMAGE_EDITOR, Panel):
    bl_label = "unf*ck"

    def draw(self, context):
        scene = context.scene
        YV_unfuck_props = scene.YV_unfuck
        
        layout = self.layout

        row = layout.row()
        row.operator("uv.youv_unfuck", text="unf*ck")

        row = layout.row()
        row.prop(YV_unfuck_props, "tension")

        row = layout.row()
        row.separator()

        row = layout.row()
        row.operator("uv.youv_straighten", text="Straighten")