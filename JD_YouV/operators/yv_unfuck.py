import bpy
import bmesh

from bpy.types import Operator

import mathutils

from . yv_util import uv_to_bmesh_selection, get_end_vertex, edge_selection_walker

class JD_Unfuck_Props(bpy.types.PropertyGroup):
    tension : bpy.props.FloatProperty(name = "Tension", min = 0, max = 1, default= .3)


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

        unfuck_props = context.scene.YV_unfuck
        tension = unfuck_props.tension

        me = bpy.context.active_object.data
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.verify()

        selected_UV_verts = []
        selected_verts = []

        for face in bm.faces:
            for loop in face.loops:
                loop_uv = loop[uv_layer]

                # print(loop_uv.uv)
                # print(loop.vert.co.xy)
                # print(loop_uv.select)

                if loop_uv.select:
                    selected_UV_verts.append(loop_uv)
                    selected_verts.append(loop.vert)

        # convert UV selection to edit mode selection
        # TODO : we should be able to do all of this via loops in UV space, no need to convert, but for now this is the mentally simpler method to understand
        uv_to_bmesh_selection(bm, me, selected_verts)

        # order vertices from one of the endpoints of the selection        
        v_start = get_end_vertex(bm)
        v_ordered = edge_selection_walker(bm, v_start)

        # first, second, second to last and last element of the sorted vertex selection
        interp_verts = [v_ordered[0], v_ordered[1], v_ordered[-2], v_ordered[-1]]
        interp_coors = []

        for vert in interp_verts:
            uv_coor = selected_UV_verts[selected_verts.index(vert)].uv
            interp_coors.append(uv_coor)

        
        bezier_coors = curve_bound_edges_to_bezier(interp_coors, len(v_ordered)-2, tension)


        # we don't need the first and last point in the selection, they only serve as guides for fixing the points between the first/last element
        v_to_fix = v_ordered[1:-1]

        for index, vert in enumerate(v_to_fix):

            # grab the indices of the selected UV vert, can appear multiple times in selected_verts (once for each loop? or Face?)
            vert_indices = [i for i, x in enumerate(selected_verts) if x == vert]

            # for each each appearance of a vertex in selected_verts, use its index to grab the relevant UV data
            for v_index in vert_indices:
                selected_UV_verts[v_index].uv = bezier_coors[index]

        # just to be safe
        bmesh.update_edit_mesh(me)

        # select everything again
        # TODO : store initial selection before running tool, restore it here
        bm.select_mode = {'VERT'}
        for v in bm.verts:
            v.select = 1
        bm.select_flush_mode()   
        bmesh.update_edit_mesh(me)

        return {'FINISHED'}


def curve_bound_edges_to_bezier(point_coors, num_bezier_points, tension):

    pos1 = point_coors[1]
    pos2 = point_coors[2]

    dir1 = point_coors[1]-point_coors[0]
    dir1 = dir1.normalized()
    dir2 = point_coors[2]-point_coors[3]
    dir2 = dir2.normalized()

    # scale tension based on the distance between end vertices
    pos_distance = pos1-pos2
    relative_tension = tension * pos_distance.length

    handle1 = pos1 + dir1 * relative_tension
    handle2 = pos2 + dir2 * relative_tension

    bezier_coors = mathutils.geometry.interpolate_bezier(pos1, handle1, handle2, pos2, num_bezier_points)

    # includes pos1 and pos2 location
    return bezier_coors


