import bpy
from .duke import CustomProperties


class NestedProps(bpy.types.PropertyGroup):
    """
    property groups declared here will be auto-registered, nested properties as well
    (see the property group below that makes use of these nested properties)
    """

    int_prop: bpy.props.IntProperty(
        name='Int property',
        description='Example integer property',
        default=10,
        min=0,
        max=100
    )


class ExampleProps(bpy.types.PropertyGroup):
    """
    property groups will be auto-registered, included nested property groups, as
    is the case with this class
    """

    nested: bpy.props.PointerProperty(
        name='Nested',
        description='Example of nested property groups',
        type=NestedProps
    )


# properties specified as CustomProperties classes will be auto-registered
example_properties = CustomProperties[
    # (owner of the property, name of the property, type (bpy.props./Property)
    (bpy.types.Object, 'example', bpy.props.PointerProperty(name='example', type=ExampleProps)),
]

# you can define as many CustomProperties classes as you wish, all will be auto-registered
example_atomic_properties = CustomProperties[
    (bpy.types.Object, 'example_atomic', bpy.props.StringProperty(name='string', description='Example string')),
]
