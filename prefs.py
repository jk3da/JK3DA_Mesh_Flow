# ============================================================
#  JK3DA MeshFlow — Preferences
# ============================================================

import bpy
from bpy.props import BoolProperty, FloatProperty, IntProperty


class JK3DAMeshFlowPrefs(bpy.types.AddonPreferences):
    """Addon preferences for MeshFlow."""
    bl_idname = __package__

    circle_regular: BoolProperty(
        name="Even Spacing by Default",
        default=True,
    )
    circle_influence: FloatProperty(
        name="Default Influence",
        default=1.0, min=0.0, max=1.0, subtype="FACTOR",
    )
    relax_iterations: IntProperty(
        name="Default Iterations",
        default=1, min=1, max=50,
    )
    relax_influence: FloatProperty(
        name="Default Influence",
        default=1.0, min=0.0, max=1.0, subtype="FACTOR",
    )
    space_influence: FloatProperty(
        name="Default Influence",
        default=1.0, min=0.0, max=1.0, subtype="FACTOR",
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "circle_regular")
        layout.prop(self, "circle_influence", slider=True)
