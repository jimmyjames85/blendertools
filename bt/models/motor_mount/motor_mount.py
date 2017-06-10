from bt import mesh, object
from bt.common import XAXIS

import bpy

def buildMotor():
    # Top view
    # 20170604_105053.jpg
    # img x=7.98, y=6.4, size = 144.2

    # Front view
    # 20170604_125026.jpg
    # img x=-1.2 y=31.5 size=144.8 rotation = 91.8

    motor = []

    # lower axis mount
    lam = mesh.newCylinder(diameter=31.5, height=11.2)
    motor.append(lam)

    # upper axis mount
    uam = mesh.newCylinder(diameter=25.4 + 1.5, height=11.2)
    mesh.transposeMesh(uam, dx=6.44, dy=13.63)
    motor.append(uam)

    # top left axis mount
    tlam = mesh.newCylinder(diameter=27.6, height=38.8)
    mesh.transposeMesh(tlam, dx=-7.12, dy=16.38, dz=-13.8)
    motor.append(tlam)

    # mounting bracket
    mb = mesh.newHexahedron(width=29.9, height=1.85, depth=27.3)
    mesh.transposeMesh(mb, dx=1.6, dy=2.28)
    motor.append(mb)

    # wheel axel
    wa = mesh.newCylinder(diameter=4, height=74)
    mesh.transposeMesh(wa, dz=10)
    motor.append(wa)

    topScrewDepth = 12.23
    topScrewDepth=10.58
    topScrewDepth=11
    topScrewDepth=11.7


    # left mounting hole
    lmh = mesh.newCylinder(diameter=3.5, height=6)
    mesh.rotateMesh(lmh, XAXIS, 90)
    mesh.transposeMesh(lmh, dx=-8.70, dy=3.94, dz=topScrewDepth)
    motor.append(lmh)

    # # left screw head
    # lsh = newCylinderMesh(diameter=5.8, height=0.5)
    # rotateMesh(lsh, XAXIS, 90)
    # transposeMesh(lsh, dx=-8.70, dy=0, dz=topScrewDepth)
    # motor.append(lsh)

    # right mounting hole
    rmh = mesh.newCylinder(diameter=3.5, height=6)
    mesh.rotateMesh(rmh, XAXIS, 90)
    mesh.transposeMesh(rmh, dx=8.70, dy=3.94, dz=topScrewDepth)
    motor.append(rmh)

    # # right screw head
    # rsh = newCylinderMesh(diameter=5.8, height=0.5)
    # rotateMesh(rsh, XAXIS, 90)
    # transposeMesh(rsh, dx=8.70, dy=0, dz=topScrewDepth)
    # motor.append(rsh)

    # bottom mounting hole
    bmh = mesh.newCylinder(diameter=3.5, height=6)
    mesh.rotateMesh(bmh, XAXIS, 90)
    mesh.transposeMesh(bmh, dx=11.20, dy=3.94, dz=-topScrewDepth)
    motor.append(bmh)

    # # bottom screw head
    # bsh = newCylinderMesh(diameter=5.8, height=0.5)
    # rotateMesh(bsh, XAXIS, 90)
    # transposeMesh(bsh, dx=11.2, dy=0, dz=-topScrewDepth)
    # motor.append(bsh)

    # join parts
    m = mesh.fromMeshes(motor)

    # clean up temporary meshes
    for tmpMesh in motor:
        bpy.data.meshes.remove(tmpMesh, do_unlink=True)

    return m


def buildMotorBase():
    base = []

    # mounting bracket
    mb = mesh.newHexahedron(width=36, height=1.85, depth=36)
    mesh.transposeMesh(mb, dx=1.6, dy=-20)
    base.append(mb)

    topScrewDepth = 12.23
    topScrewDepth=10.58
    topScrewDepth=11
    topScrewDepth=11.7

    mounting_hole_x = 8.7
    mounting_hole_height = 20
    mounting_hole_depth = -10
    mounting_hole_diameter = 6
    mounting_hole_inner_diameter = 2.6 #maybe even 2.7

    # left mounting hole
    lmh = mesh.newCylinder(diameter=mounting_hole_diameter, height=mounting_hole_height)
    mesh.rotateMesh(lmh, XAXIS, 90)
    mesh.transposeMesh(lmh, dx=-mounting_hole_x, dy=mounting_hole_depth, dz=topScrewDepth)
    base.append(lmh)

    # left mounting inner hole
    lmih = mesh.newCylinder(diameter=mounting_hole_inner_diameter, height=1.2 * mounting_hole_height)
    mesh.rotateMesh(lmih, XAXIS, 90)
    mesh.transposeMesh(lmih, dx=-mounting_hole_x, dy=mounting_hole_depth, dz=topScrewDepth)
    base.append(lmih)

    # right mounting hole
    rmh = mesh.newCylinder(diameter=mounting_hole_diameter, height=mounting_hole_height)
    mesh.rotateMesh(rmh, XAXIS, 90)
    mesh.transposeMesh(rmh, dx=mounting_hole_x, dy=mounting_hole_depth, dz=topScrewDepth)
    base.append(rmh)

    # right mounting inner hole
    rmh = mesh.newCylinder(diameter=mounting_hole_inner_diameter, height=1.2 * mounting_hole_height)
    mesh.rotateMesh(rmh, XAXIS, 90)
    mesh.transposeMesh(rmh, dx=mounting_hole_x, dy=mounting_hole_depth, dz=topScrewDepth)
    base.append(rmh)

    # bottom mounting hole
    bmh = mesh.newCylinder(diameter=mounting_hole_diameter, height=mounting_hole_height)
    mesh.rotateMesh(bmh, XAXIS, 90)
    mesh.transposeMesh(bmh, dx=11.20, dy=mounting_hole_depth, dz=-topScrewDepth)
    base.append(bmh)

    # bottom mounting inner hole
    bmih = mesh.newCylinder(diameter=mounting_hole_inner_diameter, height=1.2 * mounting_hole_height)
    mesh.rotateMesh(bmih, XAXIS, 90)
    mesh.transposeMesh(bmih, dx=11.20, dy=mounting_hole_depth, dz=-topScrewDepth)
    base.append(bmih)

    # join parts
    m = mesh.fromMeshes(base)

    # clean up temporary meshes
    for tmpMesh in base:
        bpy.data.meshes.remove(tmpMesh, do_unlink=True)

    return m



def addMotor():
    object.deleteObjIfExists("motor")
    mesh = buildMotor()
    obj = object.newObjectFromMesh("motor", mesh)
    return mesh, obj


def addMotorBase():
    object.deleteObjIfExists('motor_base')
    mesh = buildMotorBase()
    obj = object.newObjectFromMesh('motor_base', mesh)
    return mesh, obj




def main():
    # addMotor()
    return addMotorBase()

# todo
# import sys, importlib; sys.path.append('/home/jim/git/blendertools');
# from bt.models.motor_mount.motor_mount import main
# importlib.reload(main)

# import sys, importlib; sys.path.append('/home/jim/git/blendertools/models/motor_mount'); import motor_mount
# importlib.reload(motor_mount); me, obj = motor_mount.main()
