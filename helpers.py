# ============================================================
#  JK3DA MeshFlow — Math Helpers
# ============================================================

import math
import mathutils
import bmesh


def _get_selected_verts(bm):
    """Return list of selected vertices."""
    return [v for v in bm.verts if v.select and not v.hide]


def _project_to_plane(verts, normal, center):
    """Project vertices onto a plane defined by normal and center."""
    projected = []
    for v in verts:
        diff = v.co - center
        projected.append(v.co - diff.dot(normal) * normal)
    return projected


def _fit_circle_2d(points_2d):
    """
    Fit a circle to 2D points using algebraic least squares.
    Returns (cx, cy, radius).
    Own implementation — no numpy required.
    """
    n = len(points_2d)
    if n < 3:
        return 0.0, 0.0, 1.0

    # Build system: x² + y² + Dx + Ey + F = 0
    # Reformulated as: Dx + Ey + F = -(x²+y²)
    sx,  sy,  sxx, syy, sxy = 0.0, 0.0, 0.0, 0.0, 0.0
    sxr, syr, sr            = 0.0, 0.0, 0.0

    for x, y in points_2d:
        r2 = x*x + y*y
        sx  += x;    sy  += y
        sxx += x*x;  syy += y*y;  sxy += x*y
        sxr += x*r2; syr += y*r2; sr  += r2

    # 3x3 linear system via Cramer's rule
    M = [[sxx, sxy, sx],
         [sxy, syy, sy],
         [sx,  sy,  n ]]
    B = [-sxr, -syr, -sr]

    def det3(m):
        return (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])
               -m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
               +m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))

    D_main = det3(M)
    if abs(D_main) < 1e-10:
        # Degenerate — return centroid + average distance
        cx = sx / n;  cy = sy / n
        r  = sum(math.sqrt((x-cx)**2+(y-cy)**2) for x,y in points_2d) / n
        return cx, cy, r

    def replace_col(mat, col, vals):
        m = [row[:] for row in mat]
        for i in range(3):
            m[i][col] = vals[i]
        return m

    D_coef = det3(replace_col(M, 0, B))
    E_coef = det3(replace_col(M, 1, B))
    F_coef = det3(replace_col(M, 2, B))

    D = D_coef / D_main
    E = E_coef / D_main
    F = F_coef / D_main

    cx = -D / 2
    cy = -E / 2
    r2 = cx*cx + cy*cy - F
    r  = math.sqrt(max(r2, 0.0))
    return cx, cy, r


def _best_fit_normal(verts):
    """Robust best-fit plane normal using Newell's method."""
    n = mathutils.Vector((0.0, 0.0, 0.0))
    count = len(verts)
    for i in range(count):
        curr = verts[i].co
        next_ = verts[(i + 1) % count].co
        n.x += (curr.y - next_.y) * (curr.z + next_.z)
        n.y += (curr.z - next_.z) * (curr.x + next_.x)
        n.z += (curr.x - next_.x) * (curr.y + next_.y)
    if n.length < 1e-8:
        # Fallback: average face normals of linked faces
        for v in verts:
            for face in v.link_faces:
                n += face.normal
    return n.normalized() if n.length > 1e-8 else mathutils.Vector((0, 0, 1))


def _build_circle_positions(verts, bm, angle_offset=0.0,
                             custom_radius=None, regular=True, influence=1.0):
    """
    Core circle algorithm — robust for loops, rings and partial selections.

    1. Best-fit plane via Newell's method (handles any vert arrangement)
    2. Project verts to 2D plane
    3. Algebraic least-squares circle fit
    4. Redistribute by loop order (preserves topology, no twisting)
    5. Blend back with influence
    """
    if len(verts) < 3:
        return {}

    # 1. Center and plane normal
    center = sum((v.co for v in verts), mathutils.Vector()) / len(verts)
    normal = _best_fit_normal(verts)

    # 2. Build orthonormal 2D frame
    abs_n  = [abs(normal.x), abs(normal.y), abs(normal.z)]
    min_ax = abs_n.index(min(abs_n))
    ref    = mathutils.Vector((0.0, 0.0, 0.0))
    ref[min_ax] = 1.0
    u    = normal.cross(ref).normalized()
    v_ax = normal.cross(u).normalized()

    # 3. Project each vert to 2D
    pts2d = []
    for vert in verts:
        diff = vert.co - center
        pts2d.append((diff.dot(u), diff.dot(v_ax)))

    # 4. Fit circle
    cx, cy, radius = _fit_circle_2d(pts2d)
    if custom_radius is not None and custom_radius > 0:
        radius = custom_radius

    # 5. Current angle of each vert around fitted center
    raw_angles = [math.atan2(p[1] - cy, p[0] - cx) for p in pts2d]

    if regular:
        # Sort verts by current angle, then space them evenly
        # This keeps the ORDER of verts intact (no cross-connecting)
        order      = sorted(range(len(verts)), key=lambda i: raw_angles[i])
        step       = (2.0 * math.pi) / len(verts)
        base_angle = raw_angles[order[0]] + angle_offset
        # Map each vert to its evenly-spaced angle
        rank = [0] * len(verts)
        for r, idx in enumerate(order):
            rank[idx] = r
        target_angles = [base_angle + rank[i] * step for i in range(len(verts))]
    else:
        target_angles = [a + angle_offset for a in raw_angles]

    # 6. Build 3D target positions
    result = {}
    for i, vert in enumerate(verts):
        tx = cx + radius * math.cos(target_angles[i])
        ty = cy + radius * math.sin(target_angles[i])
        target = center + u * tx + v_ax * ty
        result[vert] = vert.co.lerp(target, influence)

    return result


def _sort_verts_by_loop(verts, bm):
    """
    Sort vertices by walking the edge loop.
    Uses a visited-set to prevent infinite loops on closed loops.
    Falls back to original order if walk fails.
    """
    if len(verts) < 2:
        return verts

    vert_set = set(verts)
    max_steps = len(verts) + 1  # hard limit — never exceeds vert count

    # Build adjacency within selection only
    adj = {v: [] for v in verts}
    for v in verts:
        for edge in v.link_edges:
            other = edge.other_vert(v)
            if other in vert_set:
                adj[v].append(other)

    # Prefer open-loop endpoint (1 neighbor) as start
    # For closed loops all verts have 2 neighbors — just pick first
    start = next((v for v in verts if len(adj[v]) == 1), verts[0])

    # Walk with visited tracking — no infinite loop possible
    sorted_verts = [start]
    visited      = {start}
    current      = start
    prev         = None

    for _ in range(max_steps):
        neighbors = [n for n in adj[current] if n != prev and n not in visited]
        if not neighbors:
            break
        next_v = neighbors[0]
        sorted_verts.append(next_v)
        visited.add(next_v)
        prev, current = current, next_v

    # Only use sorted result if we got all verts
    if len(sorted_verts) == len(verts):
        return sorted_verts
    return verts  # fallback — original order


def _get_boundary_verts(verts):
    """
    From a selection, return only the boundary (outer loop) verts —
    those with at least one edge connecting to a non-selected vert.
    This ensures Circle only moves the loop ring, not interior verts.
    If ALL verts are boundary (pure loop selection), return all.
    """
    sel_set = set(verts)
    boundary = [
        v for v in verts
        if any(e.other_vert(v) not in sel_set for e in v.link_edges)
    ]
    # If nothing qualifies (e.g. isolated verts), fall back to all
    return boundary if len(boundary) >= 3 else verts


def _find_endpoints(verts, bm):
    """
    Find the two best endpoints for a vert selection.
    Priority: verts with fewest selected neighbors (1 = real endpoint).
    If none found (closed loop), pick the two most distant verts.
    """
    sel_set = set(verts)

    # Build adjacency within selection only
    adj = {v: [e.other_vert(v) for e in v.link_edges
               if e.other_vert(v) in sel_set]
           for v in verts}

    # Real endpoints: 0 or 1 selected neighbor
    endpoints = [v for v in verts if len(adj[v]) <= 1]

    if len(endpoints) >= 2:
        return endpoints[0], endpoints[-1]

    # Fallback: verts with fewest neighbors (edge of the selection)
    min_n = min(len(adj[v]) for v in verts)
    candidates = [v for v in verts if len(adj[v]) == min_n]
    if len(candidates) >= 2:
        return candidates[0], candidates[-1]

    # Last resort: two most distant verts
    best_pair = (verts[0], verts[1])
    best_dist = 0.0
    for i in range(len(verts)):
        for j in range(i+1, len(verts)):
            d = (verts[i].co - verts[j].co).length
            if d > best_dist:
                best_dist = d
                best_pair = (verts[i], verts[j])
    return best_pair


def _build_edge_chains(sel_edges):
    """
    Given selected edges, split into sorted vertex chains.
    Handles multiple disconnected chains. Starts from endpoints (degree 1).
    """
    adj = {}
    for e in sel_edges:
        a, b = e.verts[0], e.verts[1]
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)

    visited_verts = set()
    chains = []

    endpoints = [v for v, nbrs in adj.items() if len(nbrs) == 1]
    if not endpoints:
        endpoints = list(adj.keys())[:1]

    def walk_chain(start):
        chain   = [start]
        visited = {start}
        current = start
        prev    = None
        while True:
            neighbors = [n for n in adj.get(current, [])
                         if n != prev and n not in visited]
            if not neighbors:
                break
            nxt = neighbors[0]
            chain.append(nxt)
            visited.add(nxt)
            prev, current = current, nxt
        return chain

    for ep in endpoints:
        if ep in visited_verts:
            continue
        chain = walk_chain(ep)
        for v in chain:
            visited_verts.add(v)
        chains.append(chain)

    for v in adj:
        if v not in visited_verts:
            chain = walk_chain(v)
            for cv in chain:
                visited_verts.add(cv)
            chains.append(chain)

    return chains
