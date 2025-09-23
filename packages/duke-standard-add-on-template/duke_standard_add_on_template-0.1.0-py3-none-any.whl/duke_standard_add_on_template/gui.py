"""
define your GUI here. All GUI (menus, panels, UI lists etc.) you define will be auto-registered by duke
"""

import bpy
from .ops import ExampleOperator
from .duke import plugin_meta

class SamplePanel(bpy.types.Panel):
    bl_label = "Example Panel"
    bl_idname = "VIEW3D_PT_sample_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = plugin_meta['name']

    def draw(self, context):
        layout = self.layout

        # reference custom properties you have defined in 'bprops.py'
        layout.prop(context.active_object, 'example')

        # wire in operators you defined in 'ops.py'
        layout.operator(ExampleOperator.bl_idname, text="Example operator button")
