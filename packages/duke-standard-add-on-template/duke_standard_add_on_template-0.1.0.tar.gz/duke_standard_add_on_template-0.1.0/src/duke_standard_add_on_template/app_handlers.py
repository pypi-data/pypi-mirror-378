"""
this file contains application handler definitions.
application handlers are functions that are fired on certain application events by Blender

functions defined in this file and matching blender app handler names will be auto-registered

please consult blender documentation regarding the required signatures of specific application handlers
"""

from bpy.app.handlers import persistent

@persistent
def load_post():
    ...
