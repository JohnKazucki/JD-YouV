import bpy
import bmesh

from bpy.types import Operator

from . yv_util import uv_selected_verts, get_UV_end_vertices, order_vertex_selection


class JD_OT_UV_straighten(Operator):
    bl_idname = "uv.youv_straighten"
    bl_label = "straighten edge"
    bl_description = "organizes vertices evenly on line between the endpoints"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        me = context.active_object.data
        bm = bmesh.from_edit_mesh(me)

        # maps vert selection to loop selection, needed for UVs later on
        vert_selection, UV_loop_selection = uv_selected_verts(bm)

        bmesh.update_edit_mesh(me)
        
        for loop_uv in UV_loop_selection:
            # print(loop_uv.select)
            pass

        # get rid of duplicate vertices, these are here due to each 3D vertex having multiple UV vertices, one per loop
        unique_vert_selection = set(vert_selection)

        end_verts = get_UV_end_vertices(bm, unique_vert_selection)


        order_vertex_selection(bm, unique_vert_selection, end_verts)                    

        return {'FINISHED'}



