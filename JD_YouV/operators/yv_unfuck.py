import bpy
import bmesh

from bpy.types import Operator

from mathutils import Vector

class JD_OT_UV_unfuck(Operator):
    bl_idname = "uv.youv_unfuck"
    bl_label = "unf*ck selection"
    bl_description = "reorganizes edges between selection along a bezier spline"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        # based on https://devtalk.blender.org/t/getting-uv-selection-data-solved/11290/2
        # and the Operator Mesh Uv template from the blender scripting editor

        me = bpy.context.active_object.data
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.verify()

        selected_verts = []

        for face in bm.faces:
            print(f"UVs in face {face.index}")

            for loop in face.loops:
                loop_uv = loop[uv_layer]

                # print(loop_uv.uv)
                # print(loop.vert.co.xy)
                # print(loop_uv.select)

                if loop_uv.select:
                    selected_verts.append(loop_uv)

                    loop_uv.uv = Vector((0, 0))

                # print(f"    - uv coordinate: {uv.co}, selection status: {uv.select}, corresponding vertex ID: {loop.vert.index}")

        print(selected_verts)
        bmesh.update_edit_mesh(me)

        return {'FINISHED'}