
# UV utility functions


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
