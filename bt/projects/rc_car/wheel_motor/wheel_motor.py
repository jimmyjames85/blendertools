from bt import mesh, object
from bt.common import XAXIS
import bpy


## TODO THIS WAS BUILT and then rotated
## TODO The top view image is really a view from the bottom
## TODO So I'm not sure about the dimensions yet
## TODO You should rebuild, and maybe take new pics
def build_motor():
    # Top view
    # 20170604_105053.jpg
    # img x=7.98, y=6.4, size = 144.2

    # Front view
    # 20170604_125026.jpg
    # img x=-1.2 y=31.5 size=144.8 rotation = 91.8

    motor = []

    # lower axis mount
    lam = mesh.newCylinder(diameter=31.5, depth=11.2)
    motor.append(lam)

    # upper axis mount
    uam = mesh.newCylinder(diameter=25.4 + 1.5, depth=11.2)
    mesh.transposeMesh(uam, dx=6.44, dy=13.63)
    motor.append(uam)

    # top left axis mount
    tlam = mesh.newCylinder(diameter=27.6, depth=38.8)
    mesh.transposeMesh(tlam, dx=-7.12, dy=16.38, dz=-13.8)
    motor.append(tlam)

    # wheel axel
    wa = mesh.newCylinder(diameter=4, depth=74)
    mesh.transposeMesh(wa, dz=10)
    motor.append(wa)

    # mounting bracket
    mb = mesh.newHexahedron(width=29.9, height=1.85, depth=27.3)
    mesh.transposeMesh(mb, dx=1.6, dy=2.28)
    # we wait to append after we cut out screw holes

    topScrewDepth = 11.7

    # left mounting hole
    lmh = mesh.newCylinder(diameter=3.5, depth=6)
    mesh.rotateMesh(lmh, XAXIS, 90)
    mesh.transposeMesh(lmh, dx=-8.70, dy=3.94, dz=topScrewDepth)
    mb = mesh.fromDifference(mb, lmh, remove_source_meshes=True)

    # # left screw head
    # lsh = newCylinderMesh(diameter=5.8, height=0.5)
    # rotateMesh(lsh, XAXIS, 90)
    # transposeMesh(lsh, dx=-8.70, dy=0, dz=topScrewDepth)
    # motor.append(lsh)

    # right mounting hole
    rmh = mesh.newCylinder(diameter=3.5, depth=6)
    mesh.rotateMesh(rmh, XAXIS, 90)
    mesh.transposeMesh(rmh, dx=8.70, dy=3.94, dz=topScrewDepth)
    mb = mesh.fromDifference(mb, rmh, remove_source_meshes=True)

    # # right screw head
    # rsh = newCylinderMesh(diameter=5.8, height=0.5)
    # rotateMesh(rsh, XAXIS, 90)
    # transposeMesh(rsh, dx=8.70, dy=0, dz=topScrewDepth)
    # motor.append(rsh)

    # bottom mounting hole
    bmh = mesh.newCylinder(diameter=3.5, depth=6)
    mesh.rotateMesh(bmh, XAXIS, 90)
    mesh.transposeMesh(bmh, dx=11.20, dy=3.94, dz=-topScrewDepth)
    mb = mesh.fromDifference(mb, bmh, remove_source_meshes=True)

    # # bottom screw head
    # bsh = newCylinderMesh(diameter=5.8, height=0.5)
    # rotateMesh(bsh, XAXIS, 90)
    # transposeMesh(bsh, dx=11.2, dy=0, dz=-topScrewDepth)
    # motor.append(bsh)

    # now we can append motor
    motor.append(mb)

    # TODO if we rebuild remove rotate see method todo above
    for me in motor:
        mesh.rotateMesh(me, XAXIS, 90)

    # join parts
    m = mesh.fromMeshes(motor)

    # clean up temporary meshes
    for tmpMesh in motor:
        bpy.data.meshes.remove(tmpMesh, do_unlink=True)

    return m


## TODO Same todo as build_motor()
def build_motor_base():
    base = []

    topScrewDepth = 11.7

    mounting_hole_x = 8.7
    mounting_hole_height = 20
    mounting_hole_depth = -10
    mounting_hole_diameter = 6
    mounting_hole_inner_diameter = 2.6  # maybe even 2.7

    # mounting bracket
    mb = mesh.newHexahedron(width=36, height=1.85, depth=36)
    mesh.transposeMesh(mb, dx=1.6, dy=-20)
    base.append(mb)

    # left mounting hole
    lmh = mesh.newCylinder(diameter=mounting_hole_diameter, depth=mounting_hole_height)
    mesh.rotateMesh(lmh, XAXIS, 90)
    mesh.transposeMesh(lmh, dx=-mounting_hole_x, dy=mounting_hole_depth, dz=topScrewDepth)
    # cut out inner hole
    lmih = mesh.newCylinder(diameter=mounting_hole_inner_diameter, depth=1.2 * mounting_hole_height)
    mesh.rotateMesh(lmih, XAXIS, 90)
    mesh.transposeMesh(lmih, dx=-mounting_hole_x, dy=mounting_hole_depth, dz=topScrewDepth)
    lmh = mesh.fromDifference(lmh, lmih, remove_source_meshes=True)
    base.append(lmh)

    # right mounting hole
    rmh = mesh.newCylinder(diameter=mounting_hole_diameter, depth=mounting_hole_height)
    mesh.rotateMesh(rmh, XAXIS, 90)
    mesh.transposeMesh(rmh, dx=mounting_hole_x, dy=mounting_hole_depth, dz=topScrewDepth)
    # cut out inner hole
    rmih = mesh.newCylinder(diameter=mounting_hole_inner_diameter, depth=1.2 * mounting_hole_height)
    mesh.rotateMesh(rmih, XAXIS, 90)
    mesh.transposeMesh(rmih, dx=mounting_hole_x, dy=mounting_hole_depth, dz=topScrewDepth)
    rmh = mesh.fromDifference(rmh, rmih, remove_source_meshes=True)
    base.append(rmh)

    # bottom mounting hole
    bmh = mesh.newCylinder(diameter=mounting_hole_diameter, depth=mounting_hole_height)
    mesh.rotateMesh(bmh, XAXIS, 90)
    mesh.transposeMesh(bmh, dx=11.20, dy=mounting_hole_depth, dz=-topScrewDepth)
    # bottom mounting inner hole
    bmih = mesh.newCylinder(diameter=mounting_hole_inner_diameter, depth=1.2 * mounting_hole_height)
    mesh.rotateMesh(bmih, XAXIS, 90)
    mesh.transposeMesh(bmih, dx=11.20, dy=mounting_hole_depth, dz=-topScrewDepth)
    bmh = mesh.fromDifference(bmh, bmih, remove_source_meshes=True)
    base.append(bmh)

    # TODO if we rebuild, remove rotate see method todo above
    for me in base:
        mesh.rotateMesh(me, XAXIS, 90)

    # join parts
    m = mesh.fromMeshes(base)

    # clean up temporary meshes
    for tmpMesh in base:
        bpy.data.meshes.remove(tmpMesh, do_unlink=True)

    return m


def new_motor_base(name="motor_base"):
    import importlib; importlib.reload(mesh)
    me = build_motor_base()
    return object.newObjectFromMesh(name, me)

def new_motor(name="wheel_motor"):
    me = build_motor()
    return object.newObjectFromMesh(name, me)


def debug_build():
    # This is so we can modify mesh library and see updates in blender
    # otherwise we have to restart blender each time we make a change to mesh.py
    import importlib;
    importlib.reload(mesh)

    object.deleteObjIfExists("wheel_motor")
    object.deleteObjIfExists("motor_base")
    # return new_motor()
    return new_motor_base()

# import sys, importlib; sys.path.append('/home/jim/git/blendertools'); from bt.projects.rc_car.wheel_motor import wheel_motor;
# print('reloading...'); importlib.reload(wheel_motor); print('loaded'); me, obj = wheel_motor.debug_build()
