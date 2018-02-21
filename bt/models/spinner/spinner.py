from bt import mesh, object
from bt.common import XAXIS, YAXIS, ZAXIS

def build_spinner_mesh():
    r = 9  # big radius
    me = mesh.newLathe(radii=[r, r, 6, 6, 4.2, 4], heights=[0, 3, 3, 4, 4, 7.5], vertCount=64)
    return me


def new_cat_spinner_cap(name="c_cap"):
    # whiskers
    whisker_width = 20
    w1 = mesh.newHexahedron(width=whisker_width, height=1.5, depth=2)
    cutout = mesh.newCylinder(radius=4, depth=15)
    w1 = mesh.fromDifference(w1, cutout, remove_source_meshes=True)

    w2 = mesh.newHexahedron(width=whisker_width, height=1.5, depth=2)
    mesh.rotateMesh(w2, ZAXIS, 20)
    cutout = mesh.newCylinder(radius=4, depth=15)
    w2 = mesh.fromDifference(w2, cutout, remove_source_meshes=True)

    w3 = mesh.newHexahedron(width=whisker_width, height=1.5, depth=2)
    mesh.rotateMesh(w3, ZAXIS, -20)
    cutout = mesh.newCylinder(radius=4, depth=15)
    w3 = mesh.fromDifference(w3, cutout, remove_source_meshes=True)

    w = mesh.fromMeshes([w1, w2, w3], remove_source_meshes=True)

    me = build_spinner_mesh()
    me = mesh.fromDifference(me, w, remove_source_meshes=True)

    obj = object.newObjectFromMesh(name, me)
    return obj


def new_spinner_cap(name="s_cap"):
    me = build_spinner_mesh()
    obj = object.newObjectFromMesh(name, me)
    return obj


def new_spinner_cap_with_initial_mesh(initial, name="s_cap_i"):
    if len(initial) != 1:
        raise Exception("Length of initial must be 1")

    sme = build_spinner_mesh()
    ime = mesh.newText(text=initial, scale=15, depth=2)
    mesh.recenter(ime)
    mesh.rotateMesh(ime, YAXIS, 180)
    me = mesh.fromDifference(sme, ime, remove_source_meshes=True)
    return me

def new_spinner_cap_with_initial(initial, name="s_cap_i"):
    me = new_spinner_cap_with_initial_mesh(initial, name)
    obj = object.newObjectFromMesh(name, me)
    return obj

def new_spinner_buttons(letters):
    distance = 30

    for i, letter in enumerate(letters):
        row = i // 4  # integer division
        col = i % 4
        name = ("letter %s [%d]" % (letter, i))
        object.deleteObjIfExists(name)
        obj = new_spinner_cap_with_initial(letter, name)
        object.translate_object(obj, dx=col * distance, dy=-row * distance)
