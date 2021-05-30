#!/usr/bin/env python3
# TODO: BLENDER OPERATORS https://docs.blender.org/api/current/bpy.ops.html
# TODO: BLENDER TYPES: https://docs.blender.org/api/current/bpy.types.html
# TODO: import bpy: run `sudo pip install fake-bpy-module-2.91` from https://github.com/nutti/fake-bpy-module
# TODO: import bpy opt #2: https://github.com/Korchy/blender_autocomplete/tree/master/2.92

# TODO
# expected naming convention
# https://blender.stackexchange.com/questions/124095/what-do-new-bpy-class-naming-conventions-in-blender-2-80-actually-mean

# TODO
# blender-basic-ui-example
# https://gist.github.com/p2or/a00bdde9f2751940717a404cf977dd01

import bpy
from bpy.types import Menu

# bl_info is a dictionary containing add-on metadata such as the title, version and author to be
# displayed in the Preferences add-on list. It also specifies the minimum Blender version required to
# run the script; older versions won’t display the add-on in the list.
bl_info = {
    "name": "jj85_scene_units_operator_info",
    "blender": (2, 82, 0),
    "category": "Object"
}


# like msgbox but with no title
def popover(text):
    bpy.context.window_manager.popover(
        (lambda self, context: self.layout.label(
            text=text)
         ))


class BT_MT_SceneUnitPie(Menu):
    bl_label = "Select Unit Pie Menu"

    def draw(self, context):
        pie = self.layout.menu_pie()

        # TODO consider sub pie menus: https://blender.stackexchange.com/questions/120237/how-would-one-code-a-pie-menu-with-an-additional-traditional-menu-beneath-it
        pie.operator_enum("object.scene_units_operator", "units")

        # manually set
        # pie.operator(operator="object.scene_units_operator",
        #                    text="default scene units OT").my_enum='TWO'


class BT_OT_SceneUnits(bpy.types.Operator):
    bl_idname = "object.scene_units_operator"
    bl_label = "set update scene units"
    bl_options = {'REGISTER', 'UNDO'}

    # Classes that contain properties from bpy.props now use Python’s type annotations (see PEP 526) and
    # should be assigned using a single colon : in Blender 2.8x instead of equals = as was done in 2.7x
    units: bpy.props.EnumProperty(
        items=(
            #(identifier, name, description, icon, number), ...

            # ('ADAPTIVE', "Adaptive", "Set scene units to ADAPTIVE"),

            # ('MICORMETERS', "Micormeters", "Set scene units to MICORMETERS"),
            ('MILLIMETERS', "Millimeters", "Set scene units to MILLIMETERS"),
            ('METERS', "Meters", "Set scene units to METERS"),
            # ('CENTIMETERS', "Centimeters", "Set scene units to CENTIMETERS"),
            # ('KILOMETERS', "Kilometers", "Set scene units to KILOMETERS"),


            ('FEET', "Feet", "Set scene units to FEET"),
            ('INCHES', "Inches", "Set scene units to INCHES"),
            # ('THOU', "Thou", "Set scene units to THOU"),
            # ('MILES', "Miles", "Set scene units to MILES"),
        ),
        default='MILLIMETERS'  # TODO: set to current state
    )

    # Notice __init__() and __del__() are declared. For other operator types they are not useful but for
    # modal operators they will be called before the Operator.invoke and after the operator finishes.
    def __init__(self):
        print("__init__")

    # destructor is useful for modal operators and is called after operator finishes
    # https://docs.blender.org/api/current/bpy.types.Operator.html#modal-execution
    def __del__(self):
        print("__destruct__")

    def log(self, text, level={'INFO'}):
        # only logs to info header if operator is modal
        self.report(level, text)

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        if self.units in ['KILOMETERS', 'METERS', 'CENTIMETERS', 'MILLIMETERS', 'MICORMETERS']:
            context.scene.unit_settings.system = 'METRIC'
        elif self.units in ['MILES', 'FEET', 'INCHES', 'THOU']:
            context.scene.unit_settings.system = 'IMPERIAL'

        context.scene.unit_settings.length_unit = self.units
        self.log("Scene units set to: %s" % str(self.units))
        return {'FINISHED'}

        # if you want to run modal
        # context.window_manager.modal_handler_add(self)
        # return {'RUNNING_MODAL'}

    # def modal(self, context, event):
    #     self.execute(context)
    #     return {'FINISHED'}
    #
    # def execute(self, context):
    #     self.log("I've Exceuted")
    #     return {'FINISHED'}


######################################################################
# returns true if data needed to be and was reloaded
def reload_texts():
    # TODO make this a plugin
    # TODO script reloader: https://blender.stackexchange.com/questions/107291/how-to-reload-all-text-editor-scripts-at-once
    ctx = bpy.context.copy()  # TODO
    ctx['area'] = ctx['screen'].areas[0]
    ret = False

    for t in bpy.data.texts:
        if t.is_modified and not t.is_in_memory:
            print("  * Warning: Updating external script", t.name)
            # Change current context to contain a TEXT_EDITOR
            oldAreaType = ctx['area'].type
            ctx['area'].type = 'TEXT_EDITOR'
            ctx['edit_text'] = t
            bpy.ops.text.resolve_conflict(ctx, resolution='RELOAD')
            # Restore context
            ctx['area'].type = oldAreaType
            ret = True
    return ret


classes = [BT_OT_SceneUnits, BT_MT_SceneUnitPie]


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
            print("registered: %s" % cls)
        except Exception as e:
            print("ERROR register: %s" % e)
    print("registerd...")


def unregister():
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
            print("unregistered: %s" % cls)
        except Exception as e:
            print("ERROR unregister: %s" % e)


def main():
    if reload_texts():
        print("reloaded")
        return

    unregister()
    register()

    # invoking menu
    bpy.ops.wm.call_menu_pie(name="BT_MT_SceneUnitPie")

    # if bpy.ops.object.scene_units_operator.poll():
    # print("invoking scen units op")
    # bpy.ops.object.scene_units_operator(
    #     'INVOKE_DEFAULT')  # calls invoke first


if __name__ == "__main__":
    register()
