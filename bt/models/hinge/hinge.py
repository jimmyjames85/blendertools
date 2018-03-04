from bt import mesh, object
from bt.common import XAXIS, YAXIS, ZAXIS
from math import sin, cos, radians, floor
import bpy
import bmesh

#
# Just so you know, You should always size your holes with proper
# clearance in your models. A 20mm hole for a 20mm part is a "size
# on size" press fit. Adding .02mm should be a snug press fit,
# 0.05mm would be a tight slip, 0.1mm a snug slip, and 0.15mm a
# free slip, and 0.4mm would give you a clearance fit for a
# bolt. Of course these dimensions vary somewhat as a percentage of
# the size of the object and the hole - (bigger needs slightly
# more), but generally a good rule of thumb.
#
# this may not be accurate, this could be affected by layer height
#
# https://www.3dhubs.com/knowledge-base/how-design-snap-fit-joints-3d-printing

def newPaperClipHinge():
    me = mesh.newHexahedron(5, 7.5, 15)

    # paperclip diam is 1.2mm

    diam = 1.2

    sizes = {5: diam + 0.2,
             2.5: diam + 0.3,
             0: diam + 0.4,
             -2.5: diam + 0.5,
             -5: diam + 0.6
             }

    # we want 0.4 for clearance !!!!!!!!!!!!!!!

    for z in sizes:
        d = sizes[z]
        cy = mesh.newCylinder(diameter=d, depth=100)
        mesh.rotateMesh(cy, YAXIS, 90)
        mesh.transposeMesh(cy, dz=z)
        me = mesh.fromDifference(me, cy, True)

    return object.newObjectFromMesh("cubey", me)

def newHingeObj(name="hinge"):


    # hinge
    scale = 0.3125
    handleLength=30 *scale
    unitDepth = 6 *scale
    innerDiam=6 *scale
    outerDiam=12 *scale
    purchase = 2 *scale
    clearance=0.4
    units = 7

    handles = []
    hinges = mesh.newHinge(units, startWithFemale=False, innerDiam=innerDiam, outerDiam=outerDiam, unitDepth=unitDepth, clearance=clearance, purchase=purchase)
    for i, h in enumerate(hinges):
        x,y,z = mesh.calculate_center(h)
        handle = mesh.newHexahedron(depth=unitDepth, width=handleLength, height=outerDiam)

        if i%2==0:
            #male
            mesh.transposeMesh(handle, dx=handleLength/2, dz=z)
            handle = mesh.fromUnion(h, handle, True)
        else:
            #female
            mesh.transposeMesh(handle, dx=-handleLength/2, dz=z)
            cutout = mesh.newCylinder(diameter=1.0001*outerDiam, depth=unitDepth*2)
            mesh.transposeMesh(cutout, dx=x, dy=y, dz=z)
            handle = mesh.fromDifference(handle, cutout, True)
            handle = mesh.fromMeshes([handle, h],True)

        handles.append(handle)



    topHandle = mesh.newHexahedron(height=outerDiam, width=outerDiam/2, depth=5.5*unitDepth)
    mesh.transposeMesh(topHandle, dx=-handleLength+outerDiam/4)
    handles.append(topHandle)

    btmHandle = mesh.newHexahedron(height=outerDiam, width=outerDiam/2, depth=7.5*unitDepth)
    mesh.transposeMesh(btmHandle, dx=handleLength-outerDiam/4)
    handles.append(btmHandle)

    me = mesh.fromMeshes(handles, True)
    mesh.rotateMesh(me, XAXIS, 90)
    mesh.makeNormalsConsistent(me)


    return object.newObjectFromMesh(name, me)

def newPillBox(name="pillbox"):

    # cell
    cellWidth = 40
    cellHeight = 30
    cellDepth = 20
    cellWallThickness = 1.2

    # hinge
    unitDepth = 2.125
    innerDiam=1.875
    outerDiam=3.75
    purchase = 0.84375
    clearance=0.4
    units = 15

    cell = mesh.newHollowBox(width=cellWidth, height=cellHeight, depth=cellDepth, wallThickness=cellWallThickness)

    hinges = mesh.newHinge(units, startWithFemale=False, innerDiam=innerDiam, outerDiam=outerDiam, unitDepth=unitDepth, clearance=clearance, purchase=purchase)
    mesh.rotateMeshes(hinges, XAXIS, 90)
    mesh.rotateMeshes(hinges, ZAXIS, 90)
    mesh.transposeMeshes(hinges, dy= (cellHeight)/2, dz=(cellDepth+outerDiam)/2 )

    # handles are what attach the hinge to the pillbox
    handles = []
    for i, h in enumerate(hinges):
        x,y,z = mesh.calculate_center(h)


        if i%2==0:
            # male
            handle = mesh.newHexahedron(depth=outerDiam + cellDepth, width=unitDepth, height=outerDiam)
            mesh.transposeMesh(handle, dx=x, dy=y, dz=(outerDiam+cellDepth)/2)
            # handle = mesh.fromUnion(h, handle, True)
            handles.append(handle)

            #
            #
            pass
        else:
            #female
            # mesh.transposeMesh(handle, dx=-handleLength/2, dz=z)
            # cutout = mesh.newCylinder(diameter=1.0001*outerDiam, depth=unitDepth*2)
            # mesh.transposeMesh(cutout, dx=x, dy=y, dz=z)
            # handle = mesh.fromDifference(handle, cutout, True)
            # handle = mesh.fromMeshes([handle, h],True)
            pass


    hndls = mesh.fromMeshes(handles, True)

    # me = mesh.fromMeshes(handles, True)
    me = mesh.fromMeshes(hinges, True)


    me = mesh.fromMeshes([me, hndls], True)
    # mesh.rotateMesh(me, XAXIS, 90)
    # mesh.rotateMesh(me, ZAXIS, 90)

    me = mesh.fromMeshes([me, cell],True)

    mesh.makeNormalsConsistent(me)


    return object.newObjectFromMesh(name, me)


# no need for console any more, use F5 to create new refresh by doing the following:
# https://blender.stackexchange.com/questions/34722/global-keyboard-shortcut-to-execute-text-editor-script
#
# Alt+F10 for fullscreen in 3D view and then F5 to refresh

# import sys, importlib; sys.path.append('/home/jim/git/blendertools'); from bt.models.hinge import hinge;
# print('reloading...'); importlib.reload(hinge); print('loaded'); obj = hinge.main()

def main():
    # This is so we can modify mesh library and see updates in blender
    # otherwise we have to restart blender each time we make a change to mesh.py
    import importlib;

    for lib in [mesh, object]:
        importlib.reload(lib)
    #
    #
    # sm = bpy.data.objects['BezierCurve']
    # mesh.codeFromObject(sm, "/tmp/tmp.py")
    # return

    # delete all objects
    for obj in bpy.data.objects:
        print(obj.name)
        if obj.name == "hinge" or obj.name=="pillbox":
            object.deleteObjIfExists(obj.name)


    return newPillBox()
