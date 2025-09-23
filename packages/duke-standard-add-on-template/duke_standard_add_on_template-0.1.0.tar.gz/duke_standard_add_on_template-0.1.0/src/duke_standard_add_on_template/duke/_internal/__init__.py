import inspect
from typing import Type, Literal, Tuple, Callable
from .._generated import meta

import bpy
import bpy_types

# --- basically all things auto-registered by the add-on framework
addon_keymaps: list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]] = []
operators: list[Type[bpy.types.Operator]] = []  # list of registered operators
panels: list[Type[bpy.types.Panel]] = []  # list of registered panels
property_groups: list[Type[bpy.types.PropertyGroup]] = []  # list of registered property groups
custom_properties: list[Type['CustomProperties']] = []  # list of registered custom properties
addon_preferences_class: type = None  # the class for this add-on's preferences
application_handlers: list[Tuple[str, Type[Callable]]] = []


class KeyCombo:
    """
    a key (mouse/keyboard etc) + optionally shift, alt, control
    """

    ctrl: bool
    shift: bool
    alt: bool
    key: str

    def __init__(self, key: str, ctrl: bool = False, shift: bool = False, alt: bool = False):
        self.key = key
        self.ctrl = ctrl
        self.shift = shift
        self.alt = alt

    @classmethod
    def parse_shortcut_expression(cls, shortcut_expression: str) -> 'KeyCombo':
        key_combo_parts = [key_combo_part.upper() for key_combo_part in shortcut_expression.split(' ') if
                           key_combo_part.isidentifier()]
        key_parts = [key_combo_part for key_combo_part in key_combo_parts if
                     key_combo_part not in {'CTRL', 'CONTROL', 'SHIFT', 'ALT'}]

        if len(key_parts) == 0:
            raise ValueError(f'must specify a key in the key combination')

        if len(key_parts) > 1:
            raise ValueError(f'too many keys specified: {key_parts}')

        return KeyCombo(
            key_parts[0],
            'CONTROL' in key_combo_parts or 'CTRL' in key_combo_parts,
            'SHIFT' in key_combo_parts,
            'ALT' in key_combo_parts
        )


class Shortcut:
    """
    a utility class that represents a shortcut, or, in other words, a combination of keys to be pressed in order to trigger an operation,
    in a certain region of a certain space
    """

    key_combo: KeyCombo  # the actual combination of keys for this shortcut
    blender_keymap: str  # the name of the standard blender keymap to use
    custom_keymap: str  # the name a custom keymap to use for this shortcut
    space: str  # the space type (VIEW_3D, CONSOLE, etc)
    region: str  # the region type (WINDOW, HEADER, etc)
    mode: str  # the shortcut mode (PRESS/RELEASE etc)

    def __init__(self,
                 key_combo: KeyCombo,
                 blender_keymap: str,
                 custom_keymap: str,
                 space_type,
                 region_type,
                 mode):
        self.key_combo = key_combo
        self.blender_keymap = blender_keymap
        self.custom_keymap = custom_keymap
        self.space = space_type
        self.region = region_type
        self.mode = mode


def load_classes(cls, module) -> list:
    """
    loads all subclasses of ``cls`` from ``module``

    :param cls: load subclasses of this cls
    :param module: look inside this module
    :return:
    """
    return [clazz for _, clazz in inspect.getmembers(module, inspect.isclass) if
            issubclass(clazz, cls) and clazz is not cls]


def register_shortcut_for_operator(shortcut_: Shortcut, operator_cls: Type[bpy.types.Operator]):
    # access default keymaps and addon keymaps
    blender_default_keymaps = bpy.context.window_manager.keyconfigs.default.keymaps
    blender_addon_keymaps = bpy.context.window_manager.keyconfigs.addon.keymaps

    # keymap values to use for registration
    keymap_name = ''
    space_type = ''
    region_type = ''

    if shortcut_.blender_keymap is not None:  # inject into an existing blender keymap
        if not shortcut_.blender_keymap in blender_default_keymaps:
            raise ValueError(
                f'supplied blender keymap {shortcut_.blender_keymap} is not a known blender keymap, intended to use custom_keymap?')

        blender_default_keymap = blender_default_keymaps[shortcut_.blender_keymap]

        keymap_name = shortcut_.blender_keymap
        space_type = blender_default_keymap.space_type
        region_type = blender_default_keymap.region_type
    else:
        keymap_name = shortcut_.custom_keymap
        space_type = shortcut_.space
        region_type = shortcut_.region

    if keymap_name in blender_addon_keymaps and \
            blender_addon_keymaps[keymap_name].space_type == space_type and \
            blender_addon_keymaps[keymap_name].region_type == region_type:
        use_keymap = blender_addon_keymaps[keymap_name]
    else:
        # if there are discrepancies, we create a new keymap
        use_keymap = blender_addon_keymaps.new(
            name=keymap_name,
            space_type=space_type,
            region_type=region_type
        )

    kmi = use_keymap.keymap_items.new(
        operator_cls.bl_idname,
        shortcut_.key_combo.key,
        shortcut_.mode,
        shift=shortcut_.key_combo.shift,
        ctrl=shortcut_.key_combo.ctrl,
        alt=shortcut_.key_combo.alt
    )

    addon_keymaps.append((use_keymap, kmi,))


def unregister_shortcuts():
    for keymap, keymap_item in addon_keymaps:
        keymap.keymap_items.remove(keymap_item)


def register_operators_with_shortcuts():
    from ... import ops
    global operators
    operators = load_classes(bpy.types.Operator, ops)

    for operator_cls in operators:
        bpy.utils.register_class(operator_cls)
        if hasattr(operator_cls, '_shortcuts'):
            for shortcut_def in operator_cls._shortcuts:
                register_shortcut_for_operator(shortcut_def, operator_cls)


def unregister_operators():
    global operators
    for operator_cls in operators:
        bpy.utils.unregister_class(operator_cls)


def register_nested_property_groups(any_class: type):
    for field, field_annotation in any_class.__annotations__.items():
        if type(field_annotation) is bpy.props._PropertyDeferred and \
                'type' in field_annotation.keywords and \
                issubclass(field_annotation.keywords['type'], bpy.types.PropertyGroup):
            register_property_group(field_annotation.keywords['type'])


def register_property_group(property_group_class: Type[bpy.types.PropertyGroup]):
    global property_groups  # the list of already registered property groups

    if property_group_class in property_groups:
        return

    register_nested_property_groups(property_group_class)
    bpy.utils.register_class(property_group_class)
    property_groups.append(property_group_class)


def register_property_groups():
    """
    registers property groups defined in props (needs special handling of nested property groups)
    """

    from ... import bprops
    user_defined_prop_groups = load_classes(bpy.types.PropertyGroup, bprops)

    for property_group_cls in user_defined_prop_groups:
        register_property_group(property_group_cls)


def unregister_property_groups():
    global property_groups
    for property_group_cls in property_groups:
        bpy.utils.unregister_class(property_group_cls)


def register_custom_properties():
    """
    registers custom properties defined in bprops.py
    """

    from ... import bprops
    global custom_properties
    custom_properties = load_classes(CustomProperties, bprops)

    for custom_properties_cls in custom_properties:
        for custom_property_def in custom_properties_cls.custom_props:
            setattr(custom_property_def[0],
                    custom_property_def[1],
                    custom_property_def[2])


def unregister_custom_properties():
    """
    unregisters custom properties defined in bprops.py
    """

    global custom_properties
    for custom_properties_cls in custom_properties:
        for custom_property_def in custom_properties_cls.custom_props:
            delattr(custom_property_def[0],
                    custom_property_def[1])


def register_ui():
    from ... import gui
    global panels
    panels = load_classes(bpy_types._GenericUI, gui)

    for panel_cls in panels:
        bpy.utils.register_class(panel_cls)


def unregister_ui():
    global panels
    for panel_cls in panels:
        bpy.utils.unregister_class(panel_cls)


def register_addon_preferences():
    from ... import addon_prefs
    preference_classes = load_classes(bpy.types.AddonPreferences, addon_prefs)

    if len(preference_classes) > 1:
        raise RuntimeError(f'expected one addon preferences class, found {len(preference_classes)} instead')

    global addon_preferences_class

    if preference_classes:
        addon_preferences_class = preference_classes[0]
    else:
        return

    # register any property groups this addon preference class might be pointing to
    register_nested_property_groups(addon_preferences_class)
    bpy.utils.register_class(addon_preferences_class)


def unregister_addon_preferences():
    global addon_preferences_class

    if addon_preferences_class is not None:
        bpy.utils.unregister_class(addon_preferences_class)


def register_application_handlers():
    """
    application handlers to register are matched by name and loaded from the app_handlers file
    """

    from ... import app_handlers
    global application_handlers

    for name, obj in inspect.getmembers(app_handlers):
        if callable(obj) and \
                hasattr(bpy.app.handlers, name) and \
                type(getattr(bpy.app.handlers, name)) is list:
            getattr(bpy.app.handlers, name).append(obj)
            application_handlers.append((name, obj))


def unregister_application_handlers():
    for handler_type, handler in application_handlers:
        handler_list = getattr(bpy.app.handlers, handler_type)
        while handler in handler_list:
            handler_list.remove(handler)


def register():
    register_addon_preferences()
    register_property_groups()
    register_custom_properties()
    register_operators_with_shortcuts()
    register_ui()
    register_application_handlers()


def unregister():
    unregister_application_handlers()
    unregister_ui()
    unregister_operators()
    unregister_custom_properties()
    unregister_property_groups()
    unregister_shortcuts()
    unregister_addon_preferences()


SpaceType = Literal[
    'EMPTY',
    'VIEW_3D',
    'IMAGE_EDITOR',
    'NODE_EDITOR',
    'SEQUENCE_EDITOR',
    'CLIP_EDITOR',
    'DOPESHEET_EDITOR',
    'GRAPH_EDITOR',
    'NLA_EDITOR',
    'TEXT_EDITOR',
    'CONSOLE',
    'INFO',
    'OUTLINER',
    'PROPERTIES',
    'FILE_BROWSER',
    'PREFERENCES'
]

RegionType = Literal[
    'WINDOW',
    'HEADER',
    'CHANNELS',
    'TEMPORARY',
    'UI',
    'TOOLS',
    'TOOL_PROPS',
    'PREVIEW',
    'HUD',
    'NAVIGATION_BAR',
    'EXECUTE',
    'FOOTER',
    'TOOL_HEADER'
]

ShortcutMode = Literal[
    'PRESS',
    'RELEASE',
    'ANY',
    'CLICK',
    'DOUBLE_CLICK',
    'CLICK_DRAG',
    'NOTHING'
]


class CustomProperties:
    custom_props: list[tuple[Type[bpy.types.ID], str, object]]

    def __class_getitem__(cls, custom_props: tuple[tuple[Type[bpy.types.ID], str, object], ...]):
        class AnonymousCustomProperties(CustomProperties):
            custom_props: list[tuple[Type[bpy.types.ID], str, object]] = []

        for custom_prop_def in custom_props:
            AnonymousCustomProperties.custom_props.append(custom_prop_def)

        return AnonymousCustomProperties


def shortcut(shortcut_expression,
             blender_keymap: str = None,
             custom_keymap: str = meta['name'],
             space_type: SpaceType = 'EMPTY',
             region_type: RegionType = 'WINDOW',
             mode: ShortcutMode = 'PRESS'):
    """
    Auto-registers a new blender keymap item to invoke this operator.

    *Example usage*::

        @shortcut('ctrl shift alt x') # registers into a custom add-on keymap

        @shortcut('ctrl x', blender_keymap = 'Window') # the shortcut will be injected in blender's 'Window' keymap

        @shortcut('ctrl shift o', custom_keymap = 'My Custom Name', space_type = 'VIEW_3D', region_type = 'HEADER') # will create a custom keymap (custom keymaps do not show up in Preferences->KeyMap menu)

    Shortcut Expression Syntax
    --------------------------

    A shortcut expression is a single string describing a key combination.
    It consists of zero or more *special keys* plus exactly one *main key*.

    Syntax
    ------

       [SPECIAL_KEY] ... KEY

    - **SPECIAL_KEY** (optional, any order, case-insensitive):

      - ``ctrl`` or ``control``
      - ``shift``
      - ``alt``

    - **KEY** (required, case-insensitive):
      Any value accepted by Blender's ``keymap_item.type``
      (e.g. letters, numbers, function keys, mouse events).

    Rules
    -----

    - At least one main **KEY** must be specified.
    - At most one main **KEY** may be specified.
    - Special keys and main key can appear in any order.
    - Special keys may be written in uppercase or lowercase.

    Examples
    --------

    - ``ctrl shift a`` → Control + Shift + A
    - ``A ctrl`` → Control + A (order doesn’t matter)
    - ``ALT F4`` → Alt + F4
    - ``mousedown ctrl`` → Control + mouse click
    - ``shift control Z`` → Control + Shift + Z

    Keymap Injection
    ----------------

    The ``@shortcut`` decorator supports two modes of keymap registration:
    **injection into existing Blender keymaps** and **creation of custom add-on keymaps**.

    Arguments
    ---------

    - **blender_keymap** (str, optional):
      Name of an existing Blender keymap.
      If supplied, this must exactly match one of Blender's built-in keymaps.
      In this case:

      - ``custom_keymap`` is ignored.
      - ``space_type`` and ``region_type`` are automatically taken from the existing keymap.

    - **custom_keymap** (str, optional):
      Name of a new keymap created specifically for the add-on.
      If supplied:

      - ``blender_keymap`` is ignored.
      - The values of ``space_type`` and ``region_type`` are used as given.

    - **space_type** (str): Editor scope of the keymap (default: ``"EMPTY"``).
    - **region_type** (str): Region scope of the keymap (default: ``"WINDOW"``).

    Defaults
    --------

    If no arguments are supplied, the following defaults apply:

    - ``blender_keymap = None``
    - ``custom_keymap = meta['name']`` (the add-on’s name)
    - ``space_type = "EMPTY"``
    - ``region_type = "WINDOW"``

    This means that by default, each shortcut is registered under a new keymap
    named after the add-on, scoped to the ``EMPTY`` space type and the ``WINDOW`` region type.

    Examples
    --------

    Inject into Blender’s built-in *3D View* keymap:

    .. code-block:: python

       @shortcut("ctrl shift x", blender_keymap="3D View")
       class ICONENGINE_OT_make_sprite(bpy.types.Operator):
           bl_idname = "iconengine.make_sprite"
           bl_label = "Make Sprite"

    Create a custom keymap for the add-on:

    .. code-block:: python

       @shortcut("alt z", custom_keymap="IconEngine", space_type="EMPTY", region_type="WINDOW")
       class ICONENGINE_OT_toggle_mode(bpy.types.Operator):
           bl_idname = "iconengine.toggle_mode"
           bl_label = "Toggle Mode"

    :param shortcut_expression: they key combination string built following the rules specified above
    :param blender_keymap: the name of an existing blender keymap to use
    :param custom_keymap: the name of the keymap into which this shortcut will be registered. you can define your own or inject into blender's existing keymaps. if you do so, space type and region type must match exactly
    :param space_type: the space type to use (VIEW_3D etc)
    :param region_type: the region type to use (WINDOW, HEADER etc)
    :param mode: the shortcut mode (PRESS/RELEASE etc)
    """

    def decorator(operator_cls):
        key_combo = KeyCombo.parse_shortcut_expression(shortcut_expression)
        if not hasattr(operator_cls, '_shortcuts'):
            operator_cls._shortcuts = []

        operator_cls._shortcuts.append(Shortcut(
            key_combo=key_combo,
            blender_keymap=blender_keymap,
            custom_keymap=custom_keymap,
            space_type=space_type,
            region_type=region_type,
            mode=mode
        ))
        return operator_cls

    return decorator
