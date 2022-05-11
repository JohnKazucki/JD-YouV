import bpy
import bmesh

from mathutils import Vector

def uv_selected_verts(bm):

    # Converts a UV selection to a set of vert indices and UV loops

    uv_layer = bm.loops.layers.uv.verify()
    bm.verts.ensure_lookup_table()

    selected_verts = []
    selected_UV_verts = []

    for vert in bm.verts:
        for loop in vert.link_loops:
            loop_uv = loop[uv_layer]
            if loop_uv.select:
                selected_verts.append(loop.vert)
                selected_UV_verts.append(loop_uv)
    
    return selected_verts, selected_UV_verts


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


def get_UV_end_vertices(bm, vert_selection):

    bm.verts.ensure_lookup_table()

    UV_end_verts = []

    for vert in vert_selection:
        selected_neighbour_verts = []
        for edge in vert.link_edges:
            
            if edge.other_vert(vert) in vert_selection:
                selected_neighbour_verts.append(edge.other_vert(vert))
            
        if len(selected_neighbour_verts) < 2:
            UV_end_verts.append(vert)

    return UV_end_verts

def order_vertex_selection(bm, vert_selection, end_verts):
    v_ordered = [end_verts[0]]

    print(vert_selection)

    for i in range(len(vert_selection)):
        print(i)
        print(v_ordered)
        vert=v_ordered[i]
        
        edges = vert.link_edges

        for edge in edges:
            other_vert = edge.other_vert(vert)

            # if the other vertex connected to this edge is in our selection from the UV editor
            # and it isn't yet in the ordered list of vertices, append it
            if other_vert in vert_selection and other_vert not in v_ordered:
                v_ordered.append(other_vert)

    return v_ordered
