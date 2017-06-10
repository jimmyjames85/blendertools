import bpy
from math import radians


def selectNone():
    bpy.ops.object.select_all(action='DESELECT')


def newObjectFromMesh(name, mesh):
    """
    addMeshObj calls bpy.data.meshes.new(name).from_pydata(verts, edges, faces)

    from_pydata(self, vertices, edges, faces)
    Make a mesh from a list of vertices/edges/faces
    Until we have a nicer way to make geometry, use this.
    :arg vertices:
       float triplets each representing (X, Y, Z)
       eg: [(0.0, 1.0, 0.5), ...].
    :type vertices: iterable object
    :arg edges:
       int pairs, each pair contains two indices to the
       *vertices* argument. eg: [(1, 2), ...]
    :type edges: iterable object
    :arg faces:
       iterator of faces, each faces contains three or more indices to
       the *vertices* argument. eg: [(5, 6, 8, 9), (1, 2, 3), ...]
    :type faces: iterable object
    .. warning::
       Invalid mesh data
       *(out of range indices, edges with matching indices,
       2 sided faces... etc)* are **not** prevented.
       If the data used for mesh creation isn't known to be valid,
       run :class:`Mesh.validate` after this function.
    """

    obj = bpy.data.objects.new(name, mesh)
    scn = bpy.context.scene
    scn.objects.link(obj)
    return obj


def rotateObj(obj, axis, deg):
    obj.rotation_euler[axis] = radians(deg)


def joinObjs(obj1, obj2):
    object.selectNone()
    scn = bpy.context.scene
    scn.objects.active = obj1
    obj1.select = True
    obj2.select = True
    bpy.ops.object.join()
    return obj1


def deleteObjIfExists(objName):
    if objName in bpy.data.objects:
        obj = bpy.data.objects[objName]
        mesh = obj.data

        # delete it
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.meshes.remove(mesh, do_unlink=True)
        return True

    return False
