from bt import mesh, object
from bt.common import XAXIS, YAXIS, ZAXIS
from math import sin, cos, radians
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


def newHinge(name="hinge"):
    innerDiam = 6
    outerDiam = 12
    unitWidth = 6
    clearance = 0.4  # clearance: 3. clear space allowed for a thing to move past or under another.
    purchase = 3  # purchase 2. a hold or position on something for applying power advantageously, or the advantage gained by such application.
    diaphragm = 1.4 # diaphragm 2. a thin sheet of material forming a partition. # the female must be wider than the male b/c the female requires a diaphragm >0


    me = []

    # todo pass in number of units
    for i in range(0, 4):

        male = mesh.newLathe(radii=[innerDiam/2, outerDiam/2,outerDiam/2,innerDiam/2], heights=[0, purchase, purchase+unitWidth, 2*purchase+unitWidth], vertCount=64)

        femaleWidth = unitWidth + diaphragm
        female = mesh.newLathe(radii=[innerDiam/2, outerDiam/2,outerDiam/2,innerDiam/2], heights=[-femaleWidth/2+purchase, -femaleWidth/2, femaleWidth/2, femaleWidth/2-purchase], vertCount=64)
        mesh.transposeMesh(female, dz=femaleWidth/2-purchase) # transpose to 0 out the starting height for the lathe
        mesh.transposeMesh(female, dz=2*(unitWidth)+clearance) # transpose for clearance


        # unit pos
        mystery = 1.8 # todo what the hell is this myster
        mesh.transposeMesh(male, dz=(2*purchase+unitWidth + mystery + clearance)*i)
        mesh.transposeMesh(female, dz=(2*purchase+unitWidth+mystery + clearance)*i)

        me.append(male)
        me.append(female)



    me = mesh.fromMeshes(me, True)



    return object.newObjectFromMesh(name, me)



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
        print (obj.name)
        if obj.name == "hinge":
            object.deleteObjIfExists(obj.name)

    return newHinge()
