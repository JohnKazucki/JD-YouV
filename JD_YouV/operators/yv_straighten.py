import bpy
import bmesh

from bpy.types import Operator

from . yv_util import uv_selected_verts, get_UV_end_vertices, order_vertex_selection, vertex_coors_to_UV


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
        
        # get rid of duplicate vertices, these are here due to each 3D vertex having multiple UV vertices, one per loop
        unique_vert_selection = set(vert_selection)

        end_verts = get_UV_end_vertices(bm, unique_vert_selection)
        ordered_verts = order_vertex_selection(bm, unique_vert_selection, end_verts)    

        adjusted_coors = space_verts_between_endpoints(ordered_verts, end_verts, vert_selection, UV_loop_selection)

        vertex_coors_to_UV(me, ordered_verts, adjusted_coors, vert_selection, UV_loop_selection)

        return {'FINISHED'}



def space_verts_between_endpoints(verts, end_verts, vert_selection, UV_loop_selection):

    end_verts_pos = []

    for vert in end_verts:
        uv_coor = UV_loop_selection[vert_selection.index(vert)].uv
        end_verts_pos.append(uv_coor)

    connecting_vector = end_verts_pos[1]-end_verts_pos[0]
    interp_coors = []

    for idx, _ in enumerate(verts):
        ratio = idx/(len(verts)-1)

        adjusted_coor = end_verts_pos[0] + connecting_vector*ratio

        interp_coors.append(adjusted_coor)

    return interp_coors