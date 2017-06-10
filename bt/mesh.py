import bpy
import bmesh
from math import sin, cos, radians
from bt import object
from bt.common import XAXIS, YAXIS, ZAXIS


def newHexahedron(width, height, depth):
    verts = []
    for x in [-width / 2, width / 2]:
        for y in [-height / 2, height / 2]:
            for z in [-depth / 2, depth / 2]:
                verts.append([x, y, z])

    faces = [(0, 1, 3, 2),
             (4, 5, 7, 6),
             (0, 2, 6, 4),
             (1, 3, 7, 5),
             (0, 1, 5, 4),
             (2, 3, 7, 6)]

    me = bpy.data.meshes.new("hexahedron")
    me.from_pydata(verts, [], faces)
    return me


def newCylinder(radius=None, diameter=None, height=None, addTopFace=True, addBottomFace=True, vertCount=16):
    if not ((radius is None) ^ (diameter is None)):
        raise Exception("Please define exactly one of radius or diameter")
    if height is None or height == 0:
        raise Exception("Invalid height")

    if diameter:
        radius = diameter / 2.0

    verts = []
    # create verts
    for z in [height / -2, height / 2]:
        for step in range(0, vertCount):
            deg = step * 360 / vertCount
            x = radius * cos(radians(deg))
            y = radius * sin(radians(deg))
            verts.append((x, y, z))

    bottom = list(range(0, vertCount))
    top = list(range(vertCount, 2 * vertCount))

    faces = []
    if addBottomFace:
        faces.append(bottom)

    if addTopFace:
        faces.append(top)

    # connect side walls
    for i in range(0, vertCount - 1):
        faces.append((bottom[i],
                      top[i],
                      top[i + 1],
                      bottom[i + 1]))

    # connect last side wall
    faces.append((bottom[vertCount - 1],
                  top[vertCount - 1],
                  top[0],
                  bottom[0]))

    me = bpy.data.meshes.new("cylinder")
    me.from_pydata(verts, [], faces)
    return me


def transposeMesh(mesh, dx=None, dy=None, dz=None):

    for v in mesh.vertices:
        if dx is not None:
            v.co[XAXIS] += dx
        if dy is not None:
            v.co[YAXIS] += dy
        if dz is not None:
            v.co[ZAXIS] += dz


def rotateMesh(mesh, axis, deg):

    tmpObj = object.newObjectFromMesh("tempForRotate", mesh)
    object.rotateObj(obj=tmpObj, axis=axis, deg=deg)
    object.selectNone()
    tmpObj.select = True
    bpy.ops.object.transform_apply(rotation=True)
    tmpMesh = fromObject(tmpObj)

    for i in range(0, len(mesh.vertices)):
        mesh.vertices[i].co[XAXIS] = tmpMesh.vertices[i].co[XAXIS]
        mesh.vertices[i].co[YAXIS] = tmpMesh.vertices[i].co[YAXIS]
        mesh.vertices[i].co[ZAXIS] = tmpMesh.vertices[i].co[ZAXIS]

    bpy.data.objects.remove(tmpObj, do_unlink=True)
    bpy.data.meshes.remove(tmpMesh, do_unlink=True)


def fromObject(obj):
    bm = bmesh.new()
    bm.from_object(obj, bpy.context.scene)
    m = bpy.data.meshes.new("meshCopy")
    bm.to_mesh(m)
    return m


def fromMeshes(meshes):
    bm = bmesh.new()

    for mesh in meshes:
        bm.from_mesh(mesh)

    m = bpy.data.meshes.new("joined")
    bm.to_mesh(m)

    return m
