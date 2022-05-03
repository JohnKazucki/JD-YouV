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

        bmesh.update_edit_mesh(me)

        bm = bmesh.from_edit_mesh(me)
        bm.select_mode = {'VERT'}
        for v in bm.verts:
            v.select = 0
            if v in selected_verts:
                v.select = 1
        bm.select_flush_mode()   
        bmesh.update_edit_mesh(me)

        uv_tails = []
        uv_starts = []

        tails = get_end_vertices(bm)
        for tail in tails:
            uv_coor = selected_UV_verts[selected_verts.index(tail)].uv
            uv_tails.append(uv_coor)


        starts = get_end_vertices(bm)
        for start in starts:
            uv_coor = selected_UV_verts[selected_verts.index(start)].uv
            uv_starts.append(uv_coor)

        bmesh.update_edit_mesh(me)

        bm.select_mode = {'VERT'}
        for v in bm.verts:
            v.select = 1
        bm.select_flush_mode()   
        bmesh.update_edit_mesh(me)

        print(uv_tails)
        print(uv_starts)

        pos1 = uv_starts[0].to_3d()
        pos2 = uv_starts[1].to_3d()

        dir1 = uv_starts[1].to_3d()-uv_tails[1].to_3d()
        dir1 = dir1.normalized()
        dir2 = uv_starts[0].to_3d()-uv_tails[0].to_3d()
        dir2 = dir2.normalized()

        handle1 = pos1 + dir1 * .1
        handle2 = pos2 + dir2 * .1


        coords = mathutils.geometry.interpolate_bezier(pos1, handle1, handle2, pos2, 4)


        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": coords})

        args = (shader, batch)

        drawhandler = bpy.types.SpaceView3D.draw_handler_add(draw, args, 'WINDOW', 'POST_VIEW')

        bmesh.update_edit_mesh(me)

        return {'FINISHED'}


def get_end_vertices(bm):
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
                print("including")
                verts.append(v)
                v.select = 0

    bm.select_flush_mode()

    print(verts)

    return verts

       
def draw(shader, batch):
    shader.bind()
    shader.uniform_float("color", (1, 1, 0, 1))
    batch.draw(shader)

    

        




def get_end_vertices_v2(bm, selected_verts, selected_UV_verts):
    # works for selections that are non cyclic in 3D space
    # how likely are cyclical selections in 3D space for this...

    # print("new run")
    
    # ends = []
    # remove = []
    # for v in selected_verts:
        
    #     point = bm.verts[v.index]
    #     n_verts = []
    #     for e in point.link_edges:
    #         other_v = e.other_vert(v)
    #         if other_v in selected_verts:
    #             n_verts.append(other_v)
    #     if len(n_verts) ==1:
    #         if v not in ends:
    #             # ends.append(v)

    #             #find the same vertex as the point in the selected verts, get its uv coor
    #             print(selected_UV_verts[selected_verts.index(v)].uv)
    #             # UV space endpoints
    #             ends.append(selected_UV_verts[selected_verts.index(v)])
    #             remove.append(v)

    # if len(ends) == 0:
    #     print("Selection is cyclic in 3D")

    # print("pre")
    # print(selected_verts)

    # for elem in remove:
    #     selected_verts.remove(elem)

    # print("post")
    # print(selected_verts)
    pass 
    
    