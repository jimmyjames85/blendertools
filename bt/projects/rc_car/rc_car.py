from requests.api import head

from bt import mesh, object
from bt.projects.rc_car.wheel_motor import wheel_motor
from bt.projects.rc_car.wheel import wheel
from bt.models.arduino_uno import arduino_uno
from bt.common import XAXIS, YAXIS, ZAXIS
import bpy


def build_battery_case():
    width = 64.1
    height = 58.2
    depth = 15.5

    switch_width = 40
    switch_height = 7

    case = mesh.newHexahedron(width=width, height=height, depth=depth)
    switch = mesh.newHexahedron(width=switch_width, height=switch_height, depth=depth / 2)

    mesh.transposeMesh(switch, dy=(height + switch_height) / 2)

    case = mesh.fromMeshes([case, switch], True)
    return case


def new_battery_case(name="battery_case"):
    me = build_battery_case()
    return object.newObjectFromMesh(name, me)


def new_wheel_motor_and_base(prefix=""):
    w = wheel.new_wheel("%s_wheel" % prefix)
    m = wheel_motor.new_motor("%s_motor" % prefix)
    mb = wheel_motor.new_motor_base("%s_motor_base" % prefix)
    object.translate_object(mb, dy=40, dz=1.2)
    object.translate_object(m, dy=40)
    wmb = object.newEmpty()
    for obj in [w, m, mb]:
        object.setParent(obj, wmb)
    return wmb


def new_rc_car(name="rc_car"):

    # https://markforged.com/blog/joinery-onyx/
    # https://coloringchaos.github.io/form-fall-16/joints

    car_width = 225
    car_length = 200
    car_center_length = car_length / 2
    car_center_width = car_width / 2

    battery_width = 64.1
    battery_height = 58.2
    battery_depth = 15.5

    base_thickness = 3
    base_width = car_length + battery_height
    base_posz = -19

    base = mesh.newHexahedron(width=base_width, height=car_width, depth=base_thickness)
    mesh.transposeMesh(base, dy=car_center_width, dx=car_center_length, dz=base_posz)

    tire_clearance_height = 47
    tire_clearance_width = 110

    # fl tire coutout
    cutout = mesh.newHexahedron(width=tire_clearance_width, height=tire_clearance_height, depth=base_thickness * 2)
    mesh.transposeMesh(cutout, dz=base_posz)
    base = mesh.fromDifference(base, cutout, True)

    # rl tire coutout
    cutout = mesh.newHexahedron(width=tire_clearance_width, height=tire_clearance_height, depth=base_thickness *2)
    mesh.transposeMesh(cutout, dx=car_length, dz=base_posz)
    base = mesh.fromDifference(base, cutout, True)

    # fr tire coutout
    cutout = mesh.newHexahedron(width=tire_clearance_width, height=tire_clearance_height, depth=base_thickness *2)
    mesh.transposeMesh(cutout, dy=car_width, dz=base_posz)
    base = mesh.fromDifference(base, cutout, True)

    # rr tire coutout
    cutout = mesh.newHexahedron(width=tire_clearance_width, height=tire_clearance_height, depth=base_thickness *2)
    mesh.transposeMesh(cutout, dx=car_length, dy=car_width, dz=base_posz)
    base = mesh.fromDifference(base, cutout, True)

    # base = mesh.fromMeshes([base, cutout], True)

    bottom = object.newObjectFromMesh("bottom", base)

    fl = new_wheel_motor_and_base("front_left")
    fr = new_wheel_motor_and_base("front_right")
    object.translate_object(fr, dy=car_width)
    object.rotateObj(fr, ZAXIS, 180)

    rl = new_wheel_motor_and_base("rear_left")
    rr = new_wheel_motor_and_base("rear_right")
    object.translate_object(rr, dy=car_width)
    object.rotateObj(rr, ZAXIS, 180)
    object.translate_object(rl, dx=car_length)
    object.translate_object(rr, dx=car_length)

    am = arduino_uno.build_arduino_uno()
    mm = arduino_uno.build_arduino_uno()
    mesh.transposeMesh(mm, dz=13)
    am = mesh.fromMeshes([am, mm], True)
    mesh.rotateMesh(am, ZAXIS, 180)
    mesh.recenter(am, dz=13)
    arduino = object.newObjectFromMesh("arduino", am)
    object.translate_object(arduino, dx=car_length, dy=car_center_width)

    bat_posz = -10
    batt1 = new_battery_case("batt_one")
    object.translate_object(batt1, dy=car_center_width, dz=bat_posz)
    object.rotateObj(batt1, ZAXIS, 90)

    batt2 = new_battery_case("batt_two")
    object.translate_object(batt2, dx=car_length, dy=car_center_width, dz=bat_posz)
    object.rotateObj(batt2, ZAXIS, 270)

    # for obj in [fl_wmb, fr_wmb]:
    #     object.translate_object(obj, dy=250)
    #     rc_car.append(obj)

    # flw, flm, flmb = new_wheel_motor_and_base("front_left")
    # frw, frm, frmb = new_wheel_motor_and_base("front_right")
    # for obj in [frmb, frm, frw]:
    #     object.translate_object(obj, dy=250)
    # c = object.calculate_center_of_objects([frw, frm, frmb])
    # empty = object.newEmpty()
    # frmb.parent = empty
    # for obj in [frmb, frm, frw]:
    #     obj.parent = empty
    # print("center is x=%s y=%s z=%s" % (c[0], c[1], c[2]))
    # "front_left_motor_base", "front_left_motor" , "front_left_wheel", "rear_left_motor_base", "rear_left_motor" , "rear_left_wheel"
    #
    # flmb = wheel_motor.new_motor_base("front_left_motor_base")
    # flm = wheel_motor.new_motor("front_left_motor")
    # flw = wheel.new_wheel("front_left_wheel")
    #
    # rlmb = wheel_motor.new_motor_base("rear_left_motor_base")
    # rlm = wheel_motor.new_motor("rear_left_motor")
    # rlw = wheel.new_wheel("rear_left_wheel")
    return [fl, fr]

def debug_build():
    # This is so we can modify mesh library and see updates in blender
    # otherwise we have to restart blender each time we make a change to mesh.py
    import importlib;
    for lib in [mesh, wheel_motor, wheel, object]:
        importlib.reload(lib)

    # delete all objects
    for obj in bpy.data.objects:
        object.deleteObjIfExists(obj.name)

    return new_rc_car()

# import sys, importlib; sys.path.append('/home/jim/git/blendertools'); from bt.projects.rc_car import rc_car;
# print('reloading...'); importlib.reload(rc_car); print('loaded'); obj = rc_car.debug_build()
