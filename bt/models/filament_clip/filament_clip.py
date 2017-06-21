from bt import mesh, object

def new_filament_clip_prusa(name="prusa_clip"):
    me = build_filament_clip(teeth_clearance=2.5)
    cutout = mesh.newHexahedron(width=5, height=8.5, depth=3)
    mesh.transposeMesh(cutout, dx=-5.5)
    me = mesh.fromDifference(me, cutout, True)

    obj = object.newObjectFromMesh(name=name, mesh=me)
    return obj

def new_filament_clip_inland(name="inland_clip"):
    me = build_filament_clip()
    obj = object.newObjectFromMesh(name=name, mesh=me)
    return obj

def build_filament_clip(filament_diameter=2.25,
                        teeth_clearance=3.9,
                        clip_height=5,
                        inner_clip_diameter=8,
                        outer_clip_diameter=16
                        ):
    '''

     - These defaults are great for Inland Printing Filament Spools

    :param filament_diameter: 1.75 is too small 2.25 works for 1.75 mm filament
    :param teeth_clearance: distance between the clamp teeth
    :param clip_height: if laid flat, how tall the clip is
    :param inner_clip_diameter:
    :param outer_clip_diameter:
    :return:
    '''

    outer_clip = mesh.newCylinder(diameter=outer_clip_diameter, height=clip_height)
    inner_clip = mesh.newCylinder(diameter=inner_clip_diameter, height=1.2 * clip_height)
    clip = mesh.fromDifference(outer_clip, inner_clip, True)
    cutout = mesh.newHexahedron(width=outer_clip_diameter, height=teeth_clearance, depth=clip_height * 1.2)

    mesh.transposeMesh(cutout, dx=-outer_clip_diameter / 2)
    clip = mesh.fromDifference(clip, cutout, True)

    # thickness: distance from inner clip wall  to outer clip wall
    thickness = (outer_clip_diameter - inner_clip_diameter) / 2
    holder = mesh.newCylinder(diameter=filament_diameter + thickness, height=clip_height)
    cutout = mesh.newCylinder(diameter=filament_diameter, height=1.2 * clip_height)
    holder = mesh.fromDifference(holder, cutout, True)

    mesh.transposeMesh(holder, dx=(outer_clip_diameter + filament_diameter + thickness / 4) / 2)

    clip = mesh.fromMeshes([holder, clip], True)

    return clip


def build_spool(outer_diameter=198, inner_diameter=55, spool_width=64, spool_wall_width=4.4):
    spool = mesh.newCylinder(diameter=outer_diameter, height=spool_width)
    spool_hole = mesh.newCylinder(diameter=inner_diameter, height=1.2 * spool_width, addTopFace=False,
                                  addBottomFace=False)
    spool_solid = mesh.fromDifference(spool, spool_hole, True)

    spool = mesh.newCylinder(diameter=1.2 * outer_diameter, height=spool_width - 2 * spool_wall_width)
    spool_hole = mesh.newCylinder(diameter=1.2 * inner_diameter, height=1.2 * spool_width)
    spool_cutout = mesh.fromDifference(spool, spool_hole, True)

    spool = mesh.fromDifference(spool_solid, spool_cutout, True)

    return spool


def new_spool(name="spool"):
    me = build_spool()
    obj = object.newObjectFromMesh(name=name, mesh=me)
    return obj
