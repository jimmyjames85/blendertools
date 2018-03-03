from bt import mesh, object
from bt.common import XAXIS, YAXIS, ZAXIS
from math import sin, cos, radians, floor
import bpy


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


def newHingeObj(name="hinge", units=5):

    scale = 1

    handleLength=30*scale
    unitDepth = 6.8*scale
    innerDiam=6*scale
    outerDiam=12*scale
    purchase = 2.7*scale
    clearance=0.4

    editMode = False # todo rm

    handles = []
    hinges = mesh.newHinge(units, startWithFemale=False, innerDiam=innerDiam, outerDiam=outerDiam, unitDepth=unitDepth, clearance=clearance, purchase=purchase)
    for i, h in enumerate(hinges):
        x,y,z = mesh.calculate_center(h)
        handle = mesh.newHexahedron(depth=unitDepth, width=handleLength, height=outerDiam)

        if i%2==0:
            #male
            mesh.transposeMesh(handle, dx=handleLength/2, dz=z)
            handle = mesh.fromUnion(h, handle, True)
            if editMode:
                mesh.transposeMesh(handle,dx=20)
        else:
            #female
            mesh.transposeMesh(handle, dx=-handleLength/2, dz=z)
            cutout = mesh.newCylinder(diameter=1.0001*outerDiam, depth=unitDepth*2)
            mesh.transposeMesh(cutout, dx=x, dy=y, dz=z)
            handle = mesh.fromDifference(handle, cutout, True)
            handle = mesh.fromMeshes([handle, h],True)

        handles.append(handle)


    if not editMode:
        topHandle = mesh.newHexahedron(height=outerDiam, width=outerDiam/2, depth=5.5*unitDepth)
        mesh.transposeMesh(topHandle, dx=-handleLength+outerDiam/4)
        handles.append(topHandle)

        btmHandle = mesh.newHexahedron(height=outerDiam, width=outerDiam/2, depth=7.5*unitDepth)
        mesh.transposeMesh(btmHandle, dx=handleLength-outerDiam/4)
        handles.append(btmHandle)

    me = mesh.fromMeshes(handles, True)

    if not editMode:
        mesh.rotateMesh(me, XAXIS, 90)


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
        if obj.name == "hinge":
            object.deleteObjIfExists(obj.name)

    return newHingeObj(units=7)
