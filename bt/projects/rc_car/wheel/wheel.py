from bt import mesh, object
from bt.common import XAXIS
import bpy

def build_wheel():
    tire_diameter = 95
    tire_height = 42
    rim_diameter = 54
    axel_diameter = 4
    axel_height = 14

    tire = mesh.newCylinder(diameter=tire_diameter, height=tire_height, vertCount=128)
    tire_cutout = mesh.newCylinder(diameter=rim_diameter, height=2*tire_height, vertCount=128)
    tire = mesh.fromDifference(tire, tire_cutout, remove_source_meshes=True)

    axel_mount = mesh.newCylinder(diameter=axel_diameter, height=axel_height)
    tire = mesh.fromUnion(tire, axel_mount, remove_source_meshes=True)

    mesh.rotateMesh(tire, XAXIS, 90)
    return tire


def new_wheel(name="wheel"):

    import importlib; importlib.reload(mesh)
    me = build_wheel()
    mesh.recenter(me)
    return object.newObjectFromMesh(name, me)




