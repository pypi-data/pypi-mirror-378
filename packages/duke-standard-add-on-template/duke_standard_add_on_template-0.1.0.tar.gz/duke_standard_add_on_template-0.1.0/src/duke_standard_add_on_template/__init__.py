from . import duke

bl_info = duke.plugin_meta


def register():
    duke.register_plugin()


def unregister():
    duke.unregister_plugin()


if __name__ == "__main__":
    duke.register_plugin()
