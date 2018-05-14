from bt import mesh, object, common
from bt.common import XAXIS, YAXIS, ZAXIS
import time
from math import sin, cos, tan, asin, acos, atan, sqrt, radians, degrees, floor
import bpy
import bmesh

# no need for console any more, use F5 to create new refresh by doing the following:
# https://blender.stackexchange.com/questions/34722/global-keyboard-shortcut-to-execute-text-editor-script
#
#
# Ctrl+Up (or Alt+F10 for fullscreen)
# then F5 to refresh
#
# User Preferences -> 3D View -> 3D View (Global) -> Add New
# Name: view3d.global_script_runner
# Key: F5 (or whatever you like)
#
# Paste the following into the text editor pane and run the script once

# import bpy, time
# class GlobalScriptRunner(bpy.types.Operator):
#     """Tooltip"""
#     bl_idname = "view3d.global_script_runner"
#     bl_label = "Global Script Runner"
#     #@classmethod
#     #def poll(cls, context):
#     #    return context.active_object is not None
#     def execute(self, context):
#         import sys, importlib; sys.path.append('/home/jim/git/blendertools'); from bt.models.hinge import hinge;
#         print('reloading...'); importlib.reload(hinge); print('loaded'); obj = hinge.main()
#         print("%f" %(time.time()))
#         return {'FINISHED'}
# def register():
#     bpy.utils.register_class(GlobalScriptRunner)
# def unregister():
#     bpy.utils.unregister_class(GlobalScriptRunner)
# if __name__ == "__main__":
#     register()


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
        x,y,z = mesh.calculate_center_of_bounding_box(h)
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
    hinge_clearance=0.4
    units = 15

    # skirt
    skirtThickness = 0.8
    skirtClearance = 0.4


    # hinges = mesh.newHingeWithHandles(units, startWithFemale=True, innerDiam=innerDiam, outerDiam=outerDiam, unitDepth=unitDepth, hinge_clearance=hinge_clearance, purchase=purchase)
    # me = mesh.fromMeshes(hinges, True)
    # return object.newObjectFromMesh(name, me)
    # # jimmy

    cell = mesh.newHollowBox(width=cellWidth, height=cellHeight, depth=cellDepth, wallThickness=cellWallThickness)

    hinges = mesh.newHinge(units, startWithFemale=False, innerDiam=innerDiam, outerDiam=outerDiam, unitDepth=unitDepth, clearance=hinge_clearance, purchase=purchase)
    mesh.rotateMeshes(hinges, YAXIS, 90)

    hingeY = (cellHeight + outerDiam) / 2 - cellWallThickness
    hingeZ = (cellDepth + outerDiam) / 2 + hinge_clearance
    mesh.transposeMeshes(hinges, dy=hingeY, dz=hingeZ)

    lidHeight = cellHeight - cellWallThickness - hinge_clearance
    lid = mesh.newHexahedron(width=cellWidth, height=lidHeight, depth=outerDiam)
    lid_hinge_clearance = outerDiam / 2 + hinge_clearance # todo this is not really the hinge_clearance between the lid and the hinge

    skirtHeight = cellHeight - 2*cellWallThickness -3*skirtClearance
    skirtWidth = cellWidth -2*cellWallThickness - 2*skirtClearance

    skirtDepth = outerDiam  + 3
    skirt_Y = 2 #todo rename
    skirt = mesh.newHollowBox(width=skirtWidth, depth=skirtDepth, height=skirtHeight, wallThickness=skirtThickness)

    mesh.rotate(lid, XAXIS, -90)
    mesh.rotate(skirt, XAXIS, -90)

    mesh.transposeMesh(lid, dy=hingeY, dz=hingeZ + lidHeight / 2 + lid_hinge_clearance )
    mesh.transposeMesh(skirt, dy=hingeY - skirt_Y, dz=hingeZ + skirtHeight / 2 + outerDiam / 2 + 2*skirtClearance)

    # closed lid
    # mesh.rotate_around(lid, XAXIS, x=0, y=hingeY, z=hingeZ, deg=-90)
    # mesh.rotate_around(skirt, XAXIS, x=0, y=hingeY, z=hingeZ, deg=-90)

    back = mesh.newHexahedron(width=cellWidth, depth=cellDepth, height=outerDiam)
    mesh.transposeMesh(back, dy=hingeY)

    # handles are what attach the hinge to the pillbox
    handles = []
    for i, h in enumerate(hinges):
        x,y,z = mesh.calculate_center_of_bounding_box(h)
        if i%2==0:
            # male
            handleHeight = lidHeight + lid_hinge_clearance
            handle = mesh.newHexahedron(depth=handleHeight, width=unitDepth, height=outerDiam)
            mesh.transposeMesh(handle, dx=x, dy=y, dz=z + handleHeight / 2)
        else:
            handle = mesh.newHexahedron(depth=outerDiam/2 + cellDepth+hinge_clearance, width=unitDepth, height=outerDiam)
            mesh.transposeMesh(handle, dx=x, dy=y, dz=z-(cellDepth+hinge_clearance)/2 - outerDiam/4)

        cutout = mesh.newCylinder(diameter=outerDiam, depth=3*unitDepth)
        mesh.rotateMesh(cutout, YAXIS, 90)
        mesh.transposeMesh(cutout, dx=x,dy=y,dz=z)
        handle = mesh.fromDifference(handle, cutout, True)

        handles.append(handle)

    me = mesh.fromMeshes(hinges + [cell,lid, back,skirt] + handles ,True)
    # PRINT
    # mesh.rotateMesh(me, XAXIS, -90)
    # mesh.transposeMesh(me, dz=cellHeight/2+outerDiam-cellWallThickness)
    # PRINT

    mesh.makeNormalsConsistent(me)

    #mesh.rotate(me, XAXIS, 15)

    return object.newObjectFromMesh(name, me)


# import sys, importlib; sys.path.append('/home/jim/git/blendertools'); from bt.models.hinge import hinge;
# print('reloading...'); importlib.reload(hinge); print('loaded'); obj = hinge.main()

def main():
    # This is so we can modify mesh library and see updates in blender
    # otherwise we have to restart blender each time we make a change to mesh.py
    import importlib;

    for lib in [mesh, object]:
        importlib.reload(lib)

    # sm = bpy.data.objects['BezierCurve']
    # mesh.codeFromObject(sm, "/tmp/tmp.py")
    # return

    # delete all objects
    for obj in bpy.data.objects:
        print(obj.name)
        if obj.name == "hinge" or obj.name=="pillbox" or obj.name=="345_triangle":
            object.deleteObjIfExists(obj.name)

    print("%f" %(time.time()))
    return newPillBox()
