# ============================================================
#  JK3DA MeshFlow — Operators
# ============================================================

import bpy
import bmesh
import mathutils

from bpy.props import BoolProperty
from .helpers import (
    _build_circle_positions,
    _build_edge_chains,
    _find_endpoints,
    _get_boundary_verts,
    _get_selected_verts,
    _sort_verts_by_loop,
)


def _apply_circle(bm, prefs):
    verts = _get_selected_verts(bm)
    verts = _get_boundary_verts(verts)
    if len(verts) < 3:
        return False

    positions = _build_circle_positions(
        verts,
        bm,
        regular=prefs.circle_regular,
        influence=prefs.circle_influence,
    )
    if not positions:
        return False

    for vert, target in positions.items():
        vert.co = target
    return True


def _apply_relax(bm, prefs):
    verts = _get_selected_verts(bm)
    if len(verts) < 2:
        return False

    iterations = max(1, prefs.relax_iterations)
    influence = max(0.0, min(1.0, prefs.relax_influence))

    for _ in range(iterations):
        targets = {}
        for vert in verts:
            neighbors = [e.other_vert(vert) for e in vert.link_edges
                         if e.other_vert(vert).select and not e.other_vert(vert).hide]
            if not neighbors:
                continue
            average = sum((n.co for n in neighbors), mathutils.Vector()) / len(neighbors)
            targets[vert] = vert.co.lerp(average, influence)

        for vert, new_co in targets.items():
            vert.co = new_co

    return True


def _sample_polyline_positions(points, is_closed):
    if len(points) < 2:
        return points

    distances = [0.0]
    for i in range(1, len(points)):
        distances.append(distances[-1] + (points[i] - points[i-1]).length)

    if is_closed:
        distances.append(distances[-1] + (points[0] - points[-1]).length)

    total = distances[-1]
    if total <= 1e-6:
        return points

    count = len(points)
    spacing = total / (count if is_closed else count - 1)
    targets = []

    for i in range(count):
        target_distance = spacing * i
        if is_closed:
            target_distance = target_distance % total

        # Find which segment contains this target distance.
        for j in range(len(points) if is_closed else len(points) - 1):
            a = points[j]
            b = points[(j + 1) % len(points)]
            seg_start = distances[j]
            seg_end = distances[(j + 1) % len(distances)] if is_closed or j + 1 < len(distances) else distances[j + 1]
            seg_len = seg_end - seg_start
            if seg_len <= 1e-6:
                continue
            if seg_start <= target_distance <= seg_end or (is_closed and target_distance < seg_end and j == len(points) - 1):
                t = (target_distance - seg_start) / seg_len
                targets.append(a.lerp(b, t))
                break
        else:
            targets.append(points[-1].copy())

    return targets


def _apply_space(bm, prefs):
    sel_edges = [e for e in bm.edges if e.select and not e.hide]
    if not sel_edges:
        return False

    chains = _build_edge_chains(sel_edges)
    if not chains:
        return False

    influence = max(0.0, min(1.0, prefs.space_influence))
    changed = False

    for chain in chains:
        if len(chain) < 2:
            continue

        sorted_chain = _sort_verts_by_loop(chain, bm)
        is_closed = any(e.other_vert(sorted_chain[-1]) == sorted_chain[0] for e in sorted_chain[-1].link_edges if e.other_vert(sorted_chain[-1]) in sorted_chain)
        points = [v.co.copy() for v in sorted_chain]
        targets = _sample_polyline_positions(points, is_closed)
        if len(targets) != len(sorted_chain):
            continue

        if not is_closed:
            # Preserve endpoints for open chains
            targets[0] = sorted_chain[0].co.copy()
            targets[-1] = sorted_chain[-1].co.copy()

        for vert, target in zip(sorted_chain, targets):
            vert.co = vert.co.lerp(target, influence)
            changed = True

    return changed


def _apply_straighten(bm, even_space=False):
    verts = _get_selected_verts(bm)
    if len(verts) < 2:
        return False

    start, end = _find_endpoints(verts, bm)
    direction = end.co - start.co
    if direction.length < 1e-6:
        return False

    direction.normalize()
    projected = []
    for vert in verts:
        distance = (vert.co - start.co).dot(direction)
        projected.append((vert, start.co + direction * distance, distance))

    if even_space and len(verts) > 1:
        projected.sort(key=lambda item: item[2])
        total = (end.co - start.co).length
        if total < 1e-6:
            return False
        for idx, (vert, _, _) in enumerate(projected):
            factor = idx / (len(projected) - 1)
            target = start.co + direction * (total * factor)
            vert.co = target
    else:
        for vert, target, _ in projected:
            vert.co = target

    return True


class JK3DA_OT_MeshFlowCircle(bpy.types.Operator):
    bl_idname = "jk3da.meshflow_circle"
    bl_label = "MeshFlow Circle"
    bl_description = "Redistribute selected mesh verts onto a best-fit circle"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        addon = __package__.split(".")[0]
        prefs = context.preferences.addons[addon].preferences
        obj = context.edit_object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)

        success = _apply_circle(bm, prefs)
        if success:
            bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
            return {"FINISHED"}

        self.report({"WARNING"}, "Select at least 3 boundary verts for circle fitting")
        return {"CANCELLED"}

    def draw(self, context):
        addon = __package__.split(".")[0]
        prefs = context.preferences.addons[addon].preferences
        layout = self.layout
        layout.prop(prefs, "circle_regular")
        layout.prop(prefs, "circle_influence", slider=True)


class JK3DA_OT_MeshFlowRelax(bpy.types.Operator):
    bl_idname = "jk3da.meshflow_relax"
    bl_label = "MeshFlow Relax"
    bl_description = "Smooth selected vertices by relaxing the selection"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        addon = __package__.split(".")[0]
        prefs = context.preferences.addons[addon].preferences
        obj = context.edit_object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)

        success = _apply_relax(bm, prefs)
        if success:
            bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
            return {"FINISHED"}

        self.report({"WARNING"}, "Select at least 2 connected verts to relax")
        return {"CANCELLED"}

    def draw(self, context):
        addon = __package__.split(".")[0]
        prefs = context.preferences.addons[addon].preferences
        layout = self.layout
        layout.prop(prefs, "relax_iterations")
        layout.prop(prefs, "relax_influence", slider=True)


class JK3DA_OT_MeshFlowSpace(bpy.types.Operator):
    bl_idname = "jk3da.meshflow_space"
    bl_label = "MeshFlow Space"
    bl_description = "Evenly distribute selected vertices along the selected edge chain"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        addon = __package__.split(".")[0]
        prefs = context.preferences.addons[addon].preferences
        obj = context.edit_object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)

        success = _apply_space(bm, prefs)
        if success:
            bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
            return {"FINISHED"}

        self.report({"WARNING"}, "Select a connected edge chain to redistribute")
        return {"CANCELLED"}

    def draw(self, context):
        addon = __package__.split(".")[0]
        prefs = context.preferences.addons[addon].preferences
        layout = self.layout
        layout.prop(prefs, "space_influence", slider=True)


class JK3DA_OT_MeshFlowStraighten(bpy.types.Operator):
    bl_idname = "jk3da.meshflow_straighten"
    bl_label = "MeshFlow Straighten"
    bl_description = "Straighten selection to a best-fit line"
    bl_options = {"REGISTER", "UNDO"}

    even_space: BoolProperty(
        name="Evenly Space",
        default=False,
    )

    def execute(self, context):
        obj = context.edit_object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)

        success = _apply_straighten(bm, self.even_space)
        if success:
            bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
            return {"FINISHED"}

        self.report({"WARNING"}, "Select at least 2 vertices for straighten")
        return {"CANCELLED"}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "even_space")
