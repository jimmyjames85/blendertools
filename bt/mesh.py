import bpy
import bmesh
from math import sin, cos, radians
from bt import object
from bt.common import XAXIS, YAXIS, ZAXIS


def remove(m, do_unlink=True):
    bpy.data.meshes.remove(m, do_unlink=do_unlink)


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


def vertsEdgesFontsFromMesh(me):
    verts = []
    for v in me.vertices:
        verts.append((v.co[XAXIS], v.co[YAXIS], v.co[ZAXIS]))

    edges = []
    for e in me.edges:
        edges.append(list(e.vertices))

    faces = []
    for f in me.polygons:
        faces.append(list(f.vertices))

    return (verts, edges, faces)


def newText(text="", scale=1, depth=1):
    if len(text) == 0:
        raise Exception("Please provide text of length > 0")

    tmpCurve = bpy.data.curves.new(type="FONT", name="tmpFontCurve")
    tmpObj = bpy.data.objects.new("myFontOb", tmpCurve)
    tmpObj.data.body = text
    tmpMesh = tmpObj.to_mesh(bpy.context.scene, False, 'PREVIEW')

    bm = bmesh.new()
    bm.from_mesh(tmpMesh)
    verts = bm.verts[:]
    bmesh.ops.scale(bm, vec=(scale, scale, 0), verts=verts)

    # extrude text

    # faces = bm.faces[:]
    #for face in faces:
        # See: https://stackoverflow.com/questions/509211/explain-slice-notation
        # r = bmesh.ops.extrude_discrete_faces(bm, faces=[face])
        # bmesh.ops.translate(bm, vec=(0, 0, depth), verts=r['faces'][0].verts)

    # https://blender.stackexchange.com/questions/49857/bmesh-extrude-face-and-end-up-with-closed-mesh
    faces = bm.faces[:]  # get a shallow copy of the array
    r  = bmesh.ops.extrude_face_region(bm, geom=faces)
    vrts = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0,0,depth), verts=vrts)


    me = bpy.data.meshes.new("textMeshCopy")
    bm.to_mesh(me)

    # clean up
    bpy.data.curves.remove(tmpCurve, do_unlink=True)
    bpy.data.objects.remove(tmpObj, do_unlink=True)
    bpy.data.meshes.remove(tmpMesh, do_unlink=True)
    return me


def newCylinder(radius=None, diameter=None, height=None, addTopFace=True, addBottomFace=True, vertCount=32):
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


def newLathe(radii=None, diameters=None, heights=None, addTopFace=True, addBottomFace=True, vertCount=32):
    if not ((radii is None) ^ (diameters is None)):
        raise Exception("Please define exactly one of radii or diameters")
    if heights is None:
        raise Exception("Please specify heights")

    if diameters is not None:
        radii = []
        for diameter in diameters:
            radii.append(diameter / 2.0)

    if len(radii) != len(heights):
        raise Exception("lists lengths must be equal")

    verts = []
    for i, z in enumerate(heights):
        radius = radii[i]
        for step in range(0, vertCount):
            deg = step * 360 / vertCount
            x = radius * cos(radians(deg))
            y = radius * sin(radians(deg))
            verts.append((x, y, z))

    faces = []

    for offset in range(0, len(radii) - 1):

        vertOffset = offset * vertCount

        bottom = list(range(vertOffset, vertOffset + vertCount))

        if addBottomFace and offset == 0:
            faces.append(bottom)

        top = list(range(vertOffset + vertCount, vertOffset + 2 * vertCount))
        if addTopFace and offset == (len(radii) - 2):
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

    me = bpy.data.meshes.new("lathe")
    me.from_pydata(verts, [], faces)

    return me


def recenter(me, dx=0, dy=0, dz=0):
    c = calculate_center(me)
    transposeMesh(me, dx=-c[XAXIS]+dx, dy=-c[YAXIS]+dy, dz=-c[ZAXIS]+dz)


def transposeMesh(theMesh, dx=None, dy=None, dz=None):
    for v in theMesh.vertices:
        if dx is not None:
            v.co[XAXIS] += dx
        if dy is not None:
            v.co[YAXIS] += dy
        if dz is not None:
            v.co[ZAXIS] += dz


def rotateMesh(theMesh, axis, deg):
    tmpObj = object.newObjectFromMesh("tempForRotate", theMesh)
    object.rotateObj(obj=tmpObj, axis=axis, deg=deg)
    object.selectNone()
    tmpObj.select = True
    bpy.ops.object.transform_apply(rotation=True)
    tmpMesh = fromObject(tmpObj)

    for i in range(0, len(theMesh.vertices)):
        theMesh.vertices[i].co[XAXIS] = tmpMesh.vertices[i].co[XAXIS]
        theMesh.vertices[i].co[YAXIS] = tmpMesh.vertices[i].co[YAXIS]
        theMesh.vertices[i].co[ZAXIS] = tmpMesh.vertices[i].co[ZAXIS]

    bpy.data.objects.remove(tmpObj, do_unlink=True)
    bpy.data.meshes.remove(tmpMesh, do_unlink=True)


def fromObject(obj):
    bm = bmesh.new()
    bm.from_object(obj, bpy.context.scene)
    m = bpy.data.meshes.new("meshCopy")
    bm.to_mesh(m)
    return m


def fromMeshes(meshes, remove_source_meshes=False):
    bm = bmesh.new()

    for m in meshes:
        bm.from_mesh(m)

    ret = bpy.data.meshes.new("joined")
    bm.to_mesh(ret)

    if remove_source_meshes:
        for t in meshes:
            bpy.data.meshes.remove(t, do_unlink=True)

    return ret


def fromBoolean(m1, m2, operation="DIFFERENCE", remove_source_meshes=False):
    '''
    :param m1:
    :param m2:
    :param operation: DIFFERENCE, INTERSECT, UNION
    :param remove_source_meshes:
    :return:
    '''

    tmpObj1 = object.newObjectFromMesh("tmp1", m1)
    tmpObj2 = object.newObjectFromMesh("tmp2", m2)

    mod1 = tmpObj1.modifiers.new(type="BOOLEAN", name="dont rely on this name USE mod1.name")
    mod1.object = tmpObj2
    mod1.operation = operation

    # TODO
    # I hate doing this; I would rather work directly on the object rather than
    # rely on the current selection which we are manipulating here
    #
    # but I couldn't get this to work
    # newMesh = tmpObj1.to_mesh(bpy.context.scene, True, settings='PREVIEW')
    #
    # :'-(
    object.selectNone()
    bpy.context.scene.objects.active = tmpObj1
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod1.name)

    newMesh = fromObject(tmpObj1)

    # clean up
    bpy.data.objects.remove(tmpObj1, do_unlink=True)
    bpy.data.objects.remove(tmpObj2, do_unlink=True)

    if remove_source_meshes:
        for m in [m1, m2]:
            bpy.data.meshes.remove(m, do_unlink=True)

    return newMesh


def calculate_center(m):
    count = len(m.vertices)
    if count == 0:
        raise Exception("No vertices in mesh")

    x_min = m.vertices[0].co[XAXIS]
    x_max = m.vertices[0].co[XAXIS]

    y_min = m.vertices[0].co[YAXIS]
    y_max = m.vertices[0].co[YAXIS]

    z_min = m.vertices[0].co[ZAXIS]
    z_max = m.vertices[0].co[ZAXIS]

    for i in range(1, len(m.vertices)):
        x = m.vertices[i].co[XAXIS]
        y = m.vertices[i].co[YAXIS]
        z = m.vertices[i].co[ZAXIS]

        if x < x_min:
            x_min = x

        if x > x_max:
            x_max = x

        if y < y_min:
            y_min = y

        if y > y_max:
            y_max = y

        if z < z_min:
            z_min = z

        if z > z_max:
            z_max = z

    return ((x_min + x_max) / 2, (y_min + y_max) / 2, (z_min + z_max) / 2)


def fromIntersection(m1, m2, remove_source_meshes=False):
    return fromBoolean(m1, m2, operation="INTERSECT", remove_source_meshes=remove_source_meshes)


def fromDifference(m1, m2, remove_source_meshes=False):
    return fromBoolean(m1, m2, operation="DIFFERENCE", remove_source_meshes=remove_source_meshes)


def fromUnion(m1, m2, remove_source_meshes=False):
    return fromBoolean(m1, m2, operation="UNION", remove_source_meshes=remove_source_meshes)
