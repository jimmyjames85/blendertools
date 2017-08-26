from bt import mesh, object
from bt.common import XAXIS, YAXIS, ZAXIS
import bpy


def newPillbox(name="pillbox"):
    # hinges
    # https://www.youtube.com/watch?v=7JhjhgjchfM
    # https://www.youtube.com/watch?v=7JhjhgjchfM

    # dad's design
    # https://linksharing.samsungcloud.com/1499724955986CyNyPgG
    boxCount = 1
    cellWallThickness = 1  # TODO

    cellWidth = 40
    cellHeight = 30
    cellDepth = 20  # cellDepth = 20

    snapClearance = 0.4  # distance between the cap and the cell when the cap is in the closed position

    axelDiameter = 2
    axelWidth = cellWidth * 0.9

    hingeDiameter = 6
    hingeSupportHeight = hingeDiameter / 2  # the extra height to support the hinge

    outerCapWidth = cellWidth - 2 * snapClearance
    outerCapHeight = cellHeight + hingeSupportHeight
    outerCapDepth = 2.5 # todo this can't get any smaller because of the axel, also this affects axel position

    hingeWidth = cellWidth * 0.7
    hingeInnerDiameter = 1.4 * axelDiameter
    hingeDY = (cellHeight + hingeDiameter) / 2 - cellWallThickness
    hingeDZ = cellDepth + outerCapDepth / 2

    innerCapWidth = cellWidth - 2 * cellWallThickness
    innerCapHeight = cellHeight - 2 * cellWallThickness
    innerCapDepth = 3  # 1.5

    innerCapWallThickness = 1.5

    capDY = 5 + cellHeight + hingeSupportHeight  # move the cap above the cell todo remove this?

    pinLockWidth = 4
    pinLockHeight = innerCapWallThickness
    pinLockDepth = 3
    pinDepth = 2*cellWallThickness

    backStopWidth=5
    backStopHeight = 0.7
    backStopDepth = 1

    pb = []

    for i in range(boxCount):
        cellDX = i * cellWidth

        # pillbox (cell)
        cell = mesh.newHollowBox(cellWidth, cellHeight, cellDepth, cellWallThickness)

        # pinLock hole
        cutout = mesh.newHexahedron(width=pinLockWidth + snapClearance,
                                    height=cellWallThickness * 3,
                                    depth=pinLockDepth + snapClearance)
        mesh.transposeMesh(cutout, dy=-cellHeight / 2,
                           dz=cellDepth/2 - (pinLockDepth + snapClearance) / 2 - innerCapDepth)
        cell = mesh.fromDifference(cell, cutout, True)

        # hinge support
        support = mesh.newHexahedron(width=cellWidth, height=hingeSupportHeight, depth=cellDepth)
        mesh.transposeMesh(support, dy=(cellHeight+hingeSupportHeight)/2 )
        cell = mesh.fromUnion(cell, support,True)


        # cap back stop (prevents lid  from falling all the way back)
        stop = mesh.newHexahedron(width=backStopWidth, height=backStopHeight, depth=cellDepth+backStopDepth)
        mesh.transposeMesh(stop, dx=(cellWidth-backStopWidth)/2,
                           dy=cellHeight/2+hingeSupportHeight+backStopHeight/2,
                           dz=backStopDepth/2)
        cell = mesh.fromMeshes([cell, stop], True)



        mesh.transposeMesh(cell, dx=cellDX, dz=cellDepth/2)
        pb.append(cell)

        # hinge
        hinge = mesh.newCylinder(diameter=hingeDiameter, depth=hingeWidth)
        # coutout barrelInnerDiameter
        hinge = mesh.fromDifference(hinge, mesh.newCylinder(diameter=hingeInnerDiameter, depth=hingeWidth * 2), True)
        # center cutout into left and right hinge
        hinge = mesh.fromDifference(hinge, mesh.newCylinder(diameter=hingeDiameter * 2, depth=hingeWidth / 3), True)
        mesh.rotateMesh(hinge, YAXIS, 90)
        # coutout slot to insert axel
        cutout = mesh.newHexahedron(width=hingeWidth * 2, height=axelDiameter, depth=hingeDiameter)
        mesh.transposeMesh(cutout, dz=hingeDiameter / 2)
        hinge = mesh.fromDifference(hinge, cutout, True)
        mesh.transposeMesh(hinge, dx=cellDX, dy=hingeDY, dz=hingeDZ)
        pb.append(hinge)

        # cap
        cap = mesh.newHexahedron(width=outerCapWidth, height=outerCapHeight, depth=outerCapDepth)
        mesh.transposeMesh(cap, dy=(outerCapHeight - cellHeight) / 2)
        innerCap = mesh.newHollowBox(width=innerCapWidth,
                                     height=innerCapHeight,
                                     depth=innerCapDepth + innerCapWallThickness,
                                     wallThickness=innerCapWallThickness)
        mesh.rotateMesh(innerCap, YAXIS, 180)
        mesh.transposeMesh(innerCap,
                           dz=-outerCapDepth / 2 - (innerCapDepth + innerCapWallThickness) / 2 + innerCapWallThickness)
        cap = mesh.fromUnion(cap, innerCap, True)
        # cutout for hinge clearance
        cutout = mesh.newHexahedron(width=hingeWidth + snapClearance,
                                    height=hingeDiameter * 1.1,
                                    depth=hingeDiameter * 1.2)
        mesh.transposeMesh(cutout, dy=(cellHeight + hingeSupportHeight) / 2)
        cap = mesh.fromDifference(cap, cutout, True)
        capThumbTab = mesh.newArc(width=cellWidth / 2, height=2, depth=0.999 * outerCapDepth)
        mesh.rotateMesh(capThumbTab, ZAXIS, 180)
        mesh.transposeMesh(capThumbTab, dy=-cellHeight / 2)
        cap = mesh.fromUnion(cap, capThumbTab, True)

        # axel
        axel = mesh.newCylinder(diameter=axelDiameter, depth=axelWidth)
        mesh.rotateMesh(axel, YAXIS, 90)
        mesh.transposeMesh(axel, dy=hingeDY)
        cap = mesh.fromUnion(cap, axel, True)

        # pin lock
        pinLock = mesh.newHexahedron(width=pinLockWidth, height=pinLockHeight, depth=pinLockDepth + snapClearance)
        lock = mesh.newPrism(width=0.999*pinLockWidth, height=0.999*pinLockDepth, depth=pinDepth)
        mesh.rotateMesh(lock, XAXIS, 90)
        mesh.transposeMesh(lock, dy=0.001 -(pinLockHeight) / 2)
        pinLock = mesh.fromUnion(pinLock, lock, True)
        mesh.transposeMesh(pinLock, dy=-(innerCapHeight - pinLockHeight) / 2,
                           dz=-(pinLockDepth + outerCapDepth + snapClearance) / 2 - innerCapDepth)
        cap = mesh.fromUnion(cap, pinLock, True)

        mesh.transposeMesh(cap, dz=cellDepth + outerCapDepth / 2)
        pb.append(cap)

        printLayout = True
        # for printing: put the cap on the floor
        if printLayout:
            for m in [cap]:
                mesh.rotateMesh(m, XAXIS, 180)
                mesh.transposeMesh(m, dx=cellDX, dy=capDY + hingeSupportHeight, dz=outerCapDepth + cellDepth)

    pb = mesh.fromMeshes(pb, True)
    return object.newObjectFromMesh(name, pb)


def main():
    # This is so we can modify mesh library and see updates in blender
    # otherwise we have to restart blender each time we make a change to mesh.py
    import importlib;
    for lib in [mesh, object]:
        importlib.reload(lib)

    # delete all objects
    for obj in bpy.data.objects:
        object.deleteObjIfExists(obj.name)

    return newPillbox()

# import sys, importlib; sys.path.append('/home/jim/git/blendertools'); from bt.models.pillbox import pillbox;
# print('reloading...'); importlib.reload(pillbox); print('loaded'); obj = pillbox.main()
