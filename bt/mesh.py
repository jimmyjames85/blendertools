import bpy
import bmesh
from math import sin, cos, radians
from bt import object
from bt.common import XAXIS, YAXIS, ZAXIS


def remove(m, do_unlink=True):
    bpy.data.meshes.remove(m, do_unlink=do_unlink)


def newFrame(width, height, depth, borderWidth, borderHeight):
    me = newHexahedron(width=width, height=height, depth=depth)
    cutout = newHexahedron(width=(width-borderWidth), height=(height-borderHeight), depth=depth*3)
    return fromDifference(me, cutout, True)

def newPrism(width, height, depth):
    verts = []

    # base
    for x in [-width / 2, width / 2]:
        for y in [-height / 2, height / 2]:
            verts.append([x, y, 0])

    verts.append([-width / 2, 0, depth])
    verts.append([width / 2, 0, depth])

    faces = [(0, 1, 3, 2),
             (0, 2, 5, 4),
             (1, 3, 5, 4),
             (0, 1, 4),
             (3, 2, 5)
             ]

    me = bpy.data.meshes.new("prism")
    me.from_pydata(verts, [], faces)
    return me

# todo rename newHollowHexahedron
# note this box is topless...
def newHollowBox(width, height, depth, wallThickness):
    innerWidth = width - 2 * wallThickness
    innerHeight = height - 2 * wallThickness
    outer = newHexahedron(width=width, height=height, depth=depth)
    inner = newHexahedron(width=innerWidth, height=innerHeight, depth=depth)
    transposeMesh(inner, dz=wallThickness)
    me = fromDifference(outer, inner, True)
    return me


# technically this is not an arc; it is a half circle skewed or squished via height
def newArc(width, height, depth, addBottomFace=True, addTopFace=True, vertCount=32):
    width /= 2

    verts = []
    # create verts
    for z in [depth / -2, depth / 2]:
        for step in range(0, vertCount):
            deg = step * 180 / (vertCount - 1)
            x = width * cos(radians(deg))
            y = height * sin(radians(deg))
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

    me = bpy.data.meshes.new("arc")
    me.from_pydata(verts, [], faces)
    return me

    pass


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

def codeFromObject(obj, fileloc, recenterOrigin=True):
    # example usage:
    # from bt.mesh import codeFromObject
    # ww = bpy.data.objects['ww']
    # 'codeFromObject(ww, "/tmp/ww.py")

    verts = []
    for v in obj.data.vertices:
        verts.append([v.co[XAXIS], v.co[YAXIS], v.co[ZAXIS]])

    faces=[]
    for srcFace in obj.data.polygons:
        face = ()
        for vi in srcFace.vertices:
            face += (vi, )
        faces.append(face)

    code = ("def new_%s(name=\"%s\"):\n" % ( obj.name, obj.name))
    code += "\tverts = [\n"
    for i, v in enumerate(verts):
        code += ("\t\t%s" % v)
        if i<=len(verts)-1:
            code += ", "
        code += "\n"
    code += "\t\t]\n"

    code += "\tfaces = [\n"
    for i, f in enumerate(faces):
        code += ("\t\t%s" % str(f))
        if i<len(faces) -1:
            code += ", "
        code += "\n"
    code += "\t\t]\n\n"

    code += "\tme = bpy.data.meshes.new(name)\n"
    code += "\tme.from_pydata(verts, [], faces)\n"
    if recenterOrigin:
        code += "\tmesh.recenter(me)\n"
    code += "\treturn me\n\n"

    f = open(fileloc, 'w')
    f.write("%s" % code)
    f.close()
    pass


def extrudeMesh(theMesh, depth, removeSourceMesh=True):

    bm = bmesh.new()
    bm.from_mesh(theMesh)

    # faces = bm.faces[:]
    # for face in faces:
    # See: https://stackoverflow.com/questions/509211/explain-slice-notation
    # r = bmesh.ops.extrude_discrete_faces(bm, faces=[face])
    # bmesh.ops.translate(bm, vec=(0, 0, depth), verts=r['faces'][0].verts)

    # https://blender.stackexchange.com/questions/49857/bmesh-extrude-face-and-end-up-with-closed-mesh
    faces = bm.faces[:]  # get a shallow copy of the array
    r = bmesh.ops.extrude_face_region(bm, geom=faces)
    vrts = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, depth), verts=vrts)

    me = bpy.data.meshes.new("extrudeCopy")
    bm.to_mesh(me)
    if removeSourceMesh:
        bpy.data.meshes.remove(theMesh, do_unlink=True)
    return me

    pass

# todo mesh.newText scale is ambigous set it to mm
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
    # for face in faces:
    # See: https://stackoverflow.com/questions/509211/explain-slice-notation
    # r = bmesh.ops.extrude_discrete_faces(bm, faces=[face])
    # bmesh.ops.translate(bm, vec=(0, 0, depth), verts=r['faces'][0].verts)

    # https://blender.stackexchange.com/questions/49857/bmesh-extrude-face-and-end-up-with-closed-mesh
    faces = bm.faces[:]  # get a shallow copy of the array
    r = bmesh.ops.extrude_face_region(bm, geom=faces)
    vrts = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, depth), verts=vrts)

    me = bpy.data.meshes.new("textMeshCopy")
    bm.to_mesh(me)

    # clean up
    bpy.data.curves.remove(tmpCurve, do_unlink=True)
    bpy.data.objects.remove(tmpObj, do_unlink=True)
    bpy.data.meshes.remove(tmpMesh, do_unlink=True)
    return me


def newCylinder(radius=None, diameter=None, depth=None, addTopFace=True, addBottomFace=True, vertCount=32):
    if not ((radius is None) ^ (diameter is None)):
        raise Exception("Please define exactly one of radius or diameter")
    if depth is None or depth == 0:
        raise Exception("Invalid depth")

    if diameter:
        radius = diameter / 2.0

    verts = []
    # create verts
    for z in [depth / -2, depth / 2]:
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

def makeNormalsConsistent(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()


def newHinge(units=5, startWithFemale=True, innerDiam=6, outerDiam=12, unitDepth=6.8, clearance=0.4, purchase=2.7):
    # diaphragm 2. a thin sheet of material forming a partition. # the female must be wider than the male b/c the female requires a diaphragm >0
    # purchase 2. a hold or position on something for applying power advantageously, or the advantage gained by such application.
    # clearance: 3. clear space allowed for a thing to move past or under another.

    # unitDepth is the visible width of each unit - it is equal to the width of the female but is only equal to the middle part of the male

    diaphragm = unitDepth - 2 * purchase
    if diaphragm<0:
        raise Exception("unitDepth must be greater than (2*purchase)")

    innerRadius = innerDiam/2
    outerRadius = outerDiam/2

    me = []

    mod=0 if startWithFemale else 1
    for i in range(0, units):
        if i % 2 == mod:
            female = newLathe(radii=[innerRadius, outerRadius, outerRadius, innerRadius], heights=[purchase, 0, 2*purchase+diaphragm,diaphragm + purchase], vertCount=64)
            transposeMesh(female, dz=purchase + (clearance + unitDepth) * i)
            me.append(female)
        else:
            male = newLathe(radii=[innerRadius, outerRadius, outerRadius, innerRadius], heights=[0, purchase, purchase + unitDepth, 2 * purchase + unitDepth], vertCount=64)
            transposeMesh(male, dz=(clearance + unitDepth) * i)
            me.append(male)

    # center at 0,0,0
    copy = fromMeshes(me)
    x,y,z = calculate_center(copy)
    remove(copy)
    for m in me:
        transposeMesh(m, dx=-x,dy=-y,dz=-z)

    return me

def recenter(me, dx=0, dy=0, dz=0):
    c = calculate_center(me)
    transposeMesh(me, dx=-c[XAXIS] + dx, dy=-c[YAXIS] + dy, dz=-c[ZAXIS] + dz)


def transposeMesh(theMesh, dx=None, dy=None, dz=None):
    for v in theMesh.vertices:
        if dx is not None:
            v.co[XAXIS] += dx
        if dy is not None:
            v.co[YAXIS] += dy
        if dz is not None:
            v.co[ZAXIS] += dz


def transposeMeshes(meshes, dx=None, dy=None, dz=None):
    for me in meshes:
        transposeMesh(me, dx,dy,dz)

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

def rotateMeshes(meshes, axis, deg):
    for me in meshes:
        rotateMesh(me, axis, deg)

def scaleMesh(theMesh, sx=1, sy=1, sz=1):
    tmpObj = object.newObjectFromMesh("tempForScale", theMesh)
    tmpObj.scale[YAXIS] = sy
    tmpObj.scale[ZAXIS] = sz
    object.selectNone()
    tmpObj.select = True
    tmpObj.scale[XAXIS] = sx
    bpy.ops.object.transform_apply(scale=True)
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
