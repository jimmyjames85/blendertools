from bt import mesh, object
from bt.projects.rc_car.wheel_motor import wheel_motor
from bt.projects.rc_car.wheel import wheel
from bt.common import XAXIS, YAXIS, ZAXIS
import bpy


def glasses_set_mesh():

    pass

def main_build():
    # This is so we can modify mesh library and see updates in blender
    # otherwise we have to restart blender each time we make a change to mesh.py
    import importlib;
    for lib in [mesh, wheel_motor, wheel, object]:
        importlib.reload(lib)

    # delete all objects
    for obj in bpy.data.objects:
        object.deleteObjIfExists(obj.name)

    return glasses_set()

# import sys, importlib; sys.path.append('/home/jim/git/blendertools'); from bt.projects.glasses import glasses;
# print('reloading...'); importlib.reload(glasses); print('loaded'); obj = glasses.main_build()
