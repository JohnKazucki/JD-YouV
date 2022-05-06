from select import select
import bpy
import bmesh

from bpy.types import Operator

import gpu
from gpu_extras.batch import batch_for_shader

import mathutils
# from mathutils import Vector

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

        
        bezier_coors = curve_bound_edges_to_bezier(interp_coors, len(v_ordered)-2)



        v_to_fix = v_ordered[1:-1]

        for index, vert in enumerate(v_to_fix):

            # grab the indices of the selected UV vert, can appear multiple times in selected_verts (once for each loop? or Face?)
            vert_indices = [i for i, x in enumerate(selected_verts) if x == vert]

            # for each each appearance of a vertex in selected_verts, use its index to grab the relevant UV data
            for v_index in vert_indices:
                selected_UV_verts[v_index].uv = bezier_coors[index]

        # just to be safe
        bmesh.update_edit_mesh(me)

        bm.select_mode = {'VERT'}
        for v in bm.verts:
            v.select = 1
        bm.select_flush_mode()   
        bmesh.update_edit_mesh(me)

        return {'FINISHED'}



def uv_to_bmesh_selection(bm, me, selected_verts):
    
    bmesh.update_edit_mesh(me)

    bm.select_mode = {'VERT'}
    for v in bm.verts:
        v.select = 0
        if v in selected_verts:
            v.select = 1
    bm.select_flush_mode()   
    bmesh.update_edit_mesh(me)

def get_end_vertex(bm):
    # works for an edit mode selection, not a UV selection

    verts=[]

    bm.select_mode = {'VERT'}

    for v in bm.verts:
        if v.select:
            n_verts = []
            for e in v.link_edges:
                if e.select:
                    n_verts.append(e)

            if len(n_verts) == 1:
                bm.select_flush_mode()
                return v

    print("ERROR: NO ENDPOINT FOUND")
    return None     

def edge_selection_walker(bm, v_start):

    # based on https://blender.stackexchange.com/questions/69796/selection-history-from-shortest-path

    verts = [v for v in bm.verts if v.select]
    v_ordered = [v_start]

    for i in range(len(verts)):
        v=v_ordered[i]
        edges = v.link_edges

        for e in edges:
            if e.select:
                vn = e.other_vert(v)
                if vn not in v_ordered:
                    v_ordered.append(vn)

    return v_ordered

def curve_bound_edges_to_bezier(point_coors, num_bezier_points):

    pos1 = point_coors[1]
    pos2 = point_coors[2]

    dir1 = point_coors[1]-point_coors[0]
    dir1 = dir1.normalized()
    dir2 = point_coors[2]-point_coors[3]
    dir2 = dir2.normalized()

    tension = 0.1

    handle1 = pos1 + dir1 * tension
    handle2 = pos2 + dir2 * tension

    bezier_coors = mathutils.geometry.interpolate_bezier(pos1, handle1, handle2, pos2, num_bezier_points)

    # includes pos1 and pos2 location
    return bezier_coors

def draw(shader, batch):
    shader.bind()
    shader.uniform_float("color", (1, 1, 0, 1))
    batch.draw(shader)

    