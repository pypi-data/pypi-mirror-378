from ._internal import register as register_plugin, unregister as unregister_plugin, CustomProperties, shortcut
from ._generated import meta as plugin_meta


def get_operators():
    """
    returns the list of operators defined by this add-on
    """

    from ._internal import operators
    return [op for op in operators]


def get_app_handlers():
    """
    returns the list of tuples (application_handler_category, application_handler_callable) for application handlers defined by this add-on
    """

    from ._internal import application_handlers
    return [(a, b,) for a, b in application_handlers]
