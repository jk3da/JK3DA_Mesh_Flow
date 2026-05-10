# ============================================================
#  JK3DA MeshFlow — Add-on Initialization
# ============================================================

bl_info = {
    "name": "JK3DA MeshFlow",
    "author": "JK3DA",
    "version": (0, 1, 0),
    "blender": (5, 1, 0),
    "location": "View3D > UI > JK3DA MeshFlow, right-click menu",
    "description": "Precision flow tools for mesh edit mode: Circle, Relax, Space, Straighten.",
    "category": "Mesh",
    "support": "COMMUNITY",
}

import bpy

from .prefs import JK3DAMeshFlowPrefs
from .ui import (
    JK3DA_PT_MeshFlow_Edit,
    JK3DA_PT_MeshFlow_Settings,
    JK3DA_MT_MeshFlow,
)
from .operators import (
    JK3DA_OT_MeshFlowCircle,
    JK3DA_OT_MeshFlowRelax,
    JK3DA_OT_MeshFlowSpace,
    JK3DA_OT_MeshFlowStraighten,
)

classes = [
    JK3DAMeshFlowPrefs,
    JK3DA_PT_MeshFlow_Edit,
    JK3DA_PT_MeshFlow_Settings,
    JK3DA_MT_MeshFlow,
    JK3DA_OT_MeshFlowCircle,
    JK3DA_OT_MeshFlowRelax,
    JK3DA_OT_MeshFlowSpace,
    JK3DA_OT_MeshFlowStraighten,
]


def _menu_draw(self, context):
    layout = self.layout
    layout.separator()
    layout.menu(JK3DA_MT_MeshFlow.bl_idname)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(_menu_draw)


def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(_menu_draw)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
