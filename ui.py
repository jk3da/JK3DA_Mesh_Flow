# ============================================================
#  JK3DA MeshFlow — UI (Panels and Menu)
# ============================================================

import bpy


class JK3DA_PT_MeshFlow_Edit(bpy.types.Panel):
    """Quick-access panel in the Edit tab — same place as LoopTools."""
    bl_label       = "JK3DA MeshFlow"
    bl_idname      = "JK3DA_PT_MeshFlow_Edit"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "JK3DA MeshFlow"
    bl_context     = "mesh_edit"

    def draw_header(self, context):
        self.layout.label(text="", icon="MESH_CIRCLE")

    def draw(self, context):
        layout = self.layout
        col    = layout.column(align=True)

        # ── Shape ────────────────────────────────────────
        col.label(text="Shape", icon="MESH_CIRCLE")
        row = col.row(align=True)
        row.scale_y = 1.3
        row.operator("jk3da.meshflow_circle", text="Circle",
                     icon="MESH_CIRCLE")

        col.separator(factor=0.6)

        # ── Flow ─────────────────────────────────────────
        col.label(text="Flow", icon="MOD_SMOOTH")
        row2 = col.row(align=True)
        row2.scale_y = 1.3
        row2.operator("jk3da.meshflow_relax", text="Relax",
                      icon="MOD_SMOOTH")
        row2.operator("jk3da.meshflow_space", text="Space",
                      icon="DRIVER_DISTANCE")

        col.separator(factor=0.6)

        # ── Align ────────────────────────────────────────
        col.label(text="Align", icon="SNAP_EDGE")
        row3 = col.row(align=True)
        row3.scale_y = 1.3
        # Straighten
        op = row3.operator("jk3da.meshflow_straighten",
                           text="Straighten", icon="SNAP_EDGE")
        op.even_space = False
        # Straighten + Space
        op2 = row3.operator("jk3da.meshflow_straighten",
                            text="Str + Space", icon="SNAP_MIDPOINT")
        op2.even_space = True


class JK3DA_PT_MeshFlow_Settings(bpy.types.Panel):
    """Settings panel in the JK3DA tab."""
    bl_label       = "MeshFlow Settings"
    bl_idname      = "JK3DA_PT_MeshFlow_Settings"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "JK3DA MeshFlow"
    bl_options     = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.label(text="", icon="MESH_CIRCLE")

    def draw(self, context):
        layout = self.layout
        addon = __package__.split(".")[0]
        prefs  = bpy.context.preferences.addons[addon].preferences

        box = layout.box()
        box.label(text="Circle", icon="MESH_CIRCLE")
        box.prop(prefs, "circle_regular")
        box.prop(prefs, "circle_influence", slider=True)

        layout.separator(factor=0.3)

        box2 = layout.box()
        box2.label(text="Relax", icon="MOD_SMOOTH")
        box2.prop(prefs, "relax_iterations")
        box2.prop(prefs, "relax_influence", slider=True)

        layout.separator(factor=0.3)

        box3 = layout.box()
        box3.label(text="Space", icon="DRIVER_DISTANCE")
        box3.prop(prefs, "space_influence", slider=True)


class JK3DA_MT_MeshFlow(bpy.types.Menu):
    """Right-click mesh menu."""
    bl_label   = "JK3DA MeshFlow"
    bl_idname  = "JK3DA_MT_MeshFlow"

    def draw(self, context):
        layout = self.layout
        layout.operator("jk3da.meshflow_circle",      text="Circle",        icon="MESH_CIRCLE")
        layout.operator("jk3da.meshflow_relax",        text="Relax",         icon="MOD_SMOOTH")
        layout.operator("jk3da.meshflow_space",        text="Space",         icon="DRIVER_DISTANCE")
        layout.separator()
        op  = layout.operator("jk3da.meshflow_straighten", text="Straighten",    icon="SNAP_EDGE")
        op.even_space = False
        op2 = layout.operator("jk3da.meshflow_straighten", text="Str + Space",   icon="SNAP_MIDPOINT")
        op2.even_space = True
