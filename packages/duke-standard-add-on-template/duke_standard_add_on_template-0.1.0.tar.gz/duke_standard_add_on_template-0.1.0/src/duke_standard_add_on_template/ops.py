import bpy
from .duke import shortcut


@shortcut('ctrl shift alt x')
class ExampleOperator(bpy.types.Operator):

    """replace this with your actual code"""

    bl_idname = "object.example_op"  # id of the operator, must be <category>.<action>
    bl_label = "Example Operator"  # shows up in menu and search
    bl_description = "Example Operator"
    bl_options = {'REGISTER', 'UNDO'}  # behavior-defining options

    @classmethod
    def poll(cls, context):
        """Operator availability check.
        Return True if the operator should be enabled, False to gray it out."""
        return context.active_object is not None

    def invoke(self, context, event):
        """Called when operator is executed via UI input (button, shortcut).
        Usually delegates to execute(), but can also show a popup or init modal logic."""
        return self.execute(context)

    def execute(self, context):
        """The actual work of the operator goes here."""
        self.report({'INFO'}, "Hello World from Example Operator!")
        return {'FINISHED'}
