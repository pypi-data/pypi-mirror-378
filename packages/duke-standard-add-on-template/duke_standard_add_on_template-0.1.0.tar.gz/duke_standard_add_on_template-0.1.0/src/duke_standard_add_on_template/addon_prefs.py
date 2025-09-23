import bpy

class ExampleAddonPreferences(bpy.types.AddonPreferences):

    bl_idname = __package__

    example_addon_property: bpy.props.StringProperty(
        name='Example Addon Property',
        description='Example Addon Property',
        default='default'
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, 'example_addon_property')
