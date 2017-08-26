from bt import mesh, object
import bpy


def cutOutPCB(pcb, cutout):
    """
    This removes both pcb and cutout mesh data and returns
    a new pcb mesh with cutout removed
    """
    newPCB = mesh.fromDifference(pcb, cutout)
    mesh.remove(pcb)
    mesh.remove(cutout)
    return newPCB


def appendPCB(pcb, appendage):
    """
    This removes both pcb and appendage mesh data and returns
    a new pcb mesh with the new appendage
    """
    newPCB = mesh.fromUnion(pcb, appendage)
    mesh.remove(pcb)
    mesh.remove(appendage)
    return newPCB


def build_arduino_uno():
    # this board is iterated at the bottom and each mesh inside is joined into one object
    board = []

    # square base recenter (0, 0) at bottom left corner of uno board
    unoWidth = 68.6
    unoHeight = 53.3
    unoDepth = 1.6
    unoPCB = mesh.newHexahedron(unoWidth, unoHeight, unoDepth)
    mesh.transposeMesh(unoPCB, dx=unoWidth / 2, dy=unoHeight / 2, dz=unoDepth / 2)

    # normally we would append the unoPCB, but first we want to cut out the screw holes
    # board.append(unoPCB)


    # mounting holes
    holeDiameter = 3

    # bottom left mounting hole
    blmhCenterX = 14
    blmhCenterY = 2.5
    blmh = mesh.newCylinder(diameter=holeDiameter, depth=3 * unoDepth)
    mesh.transposeMesh(blmh,
                       dx=blmhCenterX,
                       dy=blmhCenterY)
    unoPCB = cutOutPCB(unoPCB, blmh)

    # top left mounting hole
    tlmhCenterX = 15.3
    tlmhCenterY = 50.7
    tlmh = mesh.newCylinder(diameter=holeDiameter, depth=3 * unoDepth)
    mesh.transposeMesh(tlmh,
                       dx=tlmhCenterX,
                       dy=tlmhCenterY)

    unoPCB = cutOutPCB(unoPCB, tlmh)

    # top right mounting hole
    trmhCenterX = 66.1
    trmhCenterY = 35.5
    trmh = mesh.newCylinder(diameter=holeDiameter, depth=3 * unoDepth)
    mesh.transposeMesh(trmh,
                       dx=trmhCenterX,
                       dy=trmhCenterY)

    unoPCB = cutOutPCB(unoPCB, trmh)

    # bottom right mounting hole
    brmhCenterX = 66.1
    brmhCenterY = 7.6
    brmh = mesh.newCylinder(diameter=holeDiameter, depth=3 * unoDepth)
    mesh.transposeMesh(brmh,
                       dx=brmhCenterX,
                       dy=brmhCenterY)

    unoPCB = cutOutPCB(unoPCB, brmh)

    # now we are done modifying we can append to the board
    board.append(unoPCB)

    # usb port
    usbWidth = 16.15
    usbHeight = 12.1
    usbDepth = 10.8
    usbCenterX = 1.58
    usbCenterY = 38.1
    usbCenterZ = usbDepth / 2 + unoDepth - 0.0001  # small offset cleans up boolean union
    usbPort = mesh.newHexahedron(usbWidth, usbHeight, usbDepth)
    mesh.transposeMesh(usbPort,
                       dx=usbCenterX,
                       dy=usbCenterY,
                       dz=usbCenterZ)
    board.append(usbPort)

    # barrel jack
    bjWidth = 13.5
    bjHeight = 8.9
    bjDepth = 10.8
    bjCenterX = 4.94
    bjCenterY = 7.8
    bjCenterZ = bjDepth / 2 + unoDepth
    bj = mesh.newHexahedron(bjWidth, bjHeight, bjDepth)
    mesh.transposeMesh(bj,
                       dx=bjCenterX,
                       dy=bjCenterY,
                       dz=bjCenterZ)
    board.append(bj)

    # reset button
    rbWidth = 6.5
    rbHeight = 6.5
    rbDepth = 3.7  # 2.25 without actual button

    rbCenterX = 6.35
    rbCenterY = 49.5
    rbCenterZ = rbDepth / 2 + unoDepth

    rb = mesh.newHexahedron(rbWidth, rbHeight, rbDepth)
    mesh.transposeMesh(rb,
                       dx=rbCenterX,
                       dy=rbCenterY,
                       dz=rbCenterZ)
    board.append(rb)

    # bottom pin row
    bprWidth = 38.6
    bprHeight = 2.55
    bprDepth = 10.3
    bprCenterX = 45.75
    bprCenterY = 2.5
    bprCenterZ = bprDepth / 2 + unoDepth
    bpr = mesh.newHexahedron(bprWidth, bprHeight, bprDepth)
    mesh.transposeMesh(bpr,
                       dx=bprCenterX,
                       dy=bprCenterY,
                       dz=bprCenterZ)
    board.append(bpr)

    # bottom pin row
    tprWidth = 47.85
    tprHeight = 2.55
    tprDepth = 10.3
    tprCenterX = 41.12
    tprCenterY = 50.7
    tprCenterZ = tprDepth / 2 + unoDepth
    tpr = mesh.newHexahedron(tprWidth, tprHeight, tprDepth)
    mesh.transposeMesh(tpr,
                       dx=tprCenterX,
                       dy=tprCenterY,
                       dz=tprCenterZ)
    board.append(tpr)

    # join parts
    ret = mesh.fromMeshes(board)

    # clean up temporary meshes
    for tmpMesh in board:
        bpy.data.meshes.remove(tmpMesh, do_unlink=True)

    return ret


def new_arduino_uno(name="arduino_uno"):
    pcbMesh = build_arduino_uno()
    obj = object.newObjectFromMesh(name, pcbMesh)
    return obj


def main(name="arduino_uno"):
    import importlib;
    importlib.reload(mesh)  # todo remove this

    object.deleteObjIfExists(name)
    pcbMesh = build_arduino_uno()

    obj = object.newObjectFromMesh(name, pcbMesh)
    object.selectNone()

    return pcbMesh, obj

    # import sys, importlib; sys.path.append('/home/jim/git/blendertools'); from bt.models.arduino_uno import arduino_uno;
    # print('reloading...'); importlib.reload(arduino_uno); print('loaded'); me, obj = arduino_uno.main()
