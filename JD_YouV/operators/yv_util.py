
import bpy
import bmesh

# UV utility functions


def uv_selected_verts(bm):

    # Converts a UV selection to a set of vert indices and associated UV loops
    # Includes duplicate vertex IDs, one for each loop it is connected to (critical for modifying UVs via vertices)

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


def get_UV_end_vertices(bm, vert_selection):

    # NOTE :  ONLY WORKS AS INTENDED FOR A SINGLE LOOP OF VERTICES

    # go over each vertex in the selection
    # via its connected edges, find neighbouring vertices
    # count how many neighbours are in the selection
    # if only 1 neighbour in the selection, we've found an "endpoint" of our selection

    bm.verts.ensure_lookup_table()

    UV_end_verts = []

    for vert in vert_selection:
        selected_neighbour_verts = []
        for edge in vert.link_edges:
            
            if edge.other_vert(vert) in vert_selection:
                selected_neighbour_verts.append(edge.other_vert(vert))
            
        # if the current vertex has less than 2 neighbours in the selection, it must be an "endpoint"
        if len(selected_neighbour_verts) < 2:
            UV_end_verts.append(vert)

    return UV_end_verts


def order_vertex_selection(bm, vert_selection, end_verts):

    # NOTE :  ONLY WORKS AS INTENDED FOR A SINGLE LOOP OF VERTICES

    # use one of the endpoint vertices as the starting point to order our selection
    # find its linked edges, find the other vertex connected to that edge
    # if that vertex isn't already in the selection, append it to our ordered list of vertices
    # in the next iteration of the for loop, we will search for the linked edges of the newly added vertex
    
    v_ordered = [end_verts[0]]

    for i in range(len(vert_selection)):

        vert=v_ordered[i]
        
        edges = vert.link_edges

        for edge in edges:
            other_vert = edge.other_vert(vert)

            # if the other vertex connected to this edge is in our selection from the UV editor
            # and it isn't yet in the ordered list of vertices, append it
            if other_vert in vert_selection and other_vert not in v_ordered:
                v_ordered.append(other_vert)

    return v_ordered


def vertex_coors_to_UV(me, v_to_fix, fixed_coors, vert_selection, uv_loop_selection):

    for idx, vert in enumerate(v_to_fix):
        
        # grab the indices of the selected UV vert, can appear multiple times in selected_verts (once for each loop? or Face?)
        vert_indices = [i for i, x in enumerate(vert_selection) if x == vert]

        # for each each appearance of a vertex in selected_verts, use its index to grab the relevant UV data
        for v_index in vert_indices:
            uv_loop_selection[v_index].uv = fixed_coors[idx]

        # UV changes require an update of the bmesh
        bmesh.update_edit_mesh(me)