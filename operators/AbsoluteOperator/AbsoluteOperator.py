#!/usr/bin/env python3
# TODO: BLENDER OPERATORS https://docs.blender.org/api/current/bpy.ops.html
# TODO: BLENDER TYPES: https://docs.blender.org/api/current/bpy.types.html
# TODO: import bpy: run `sudo pip install fake-bpy-module-2.91` from https://github.com/nutti/fake-bpy-module
# TODO: import bpy opt #2: https://github.com/Korchy/blender_autocomplete/tree/master/2.92

# TODO: next operator idea: always draw coordinates on 3D View for selected active object / vert (maybe as an overlay?)

# TODO: is key free, don't override blender keyshortcut https://docs.blender.org/manual/en/latest/addons/development/is_key_free.html

# TODO: next plugin/ key shortcut switch to millimeters/ft etc...

# garbage pail top diam 170mm bto 120mm height 200m

import sys
import time
import bpy
import bmesh
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader

bl_info = {
    "name": "jimmyjames_bl_info",
    "blender": (2, 82, 0),
    "category": "Object"
}


# like msgbox but with no title
def popover(text):
    bpy.context.window_manager.popover(
        (lambda self, context: self.layout.label(
            text=text)
         ))


def msgbox(text, title='MsgBox', icon='INFO'):
    bpy.context.window_manager.popup_menu(
        (lambda self, context: self.layout.label(
            text=text)
         ), title=title, icon=icon)


class AbsoulteOperator(bpy.types.Operator):
    # TODO Rename everything
    bl_idname = "object.absolute_operator"
    bl_label = "set absolute positional value"
    bl_options = {'REGISTER'}

    user_input = ""
    axis = None
    sign = float(1.0)
    mouse_path = []

    def __init__(self):
        print("initringg....")

    # destructor is useful for modal operators and is called after operator finishes
    # https://docs.blender.org/api/current/bpy.types.Operator.html#modal-execution
    def __del__(self):
        print("destruct me")
        self.unregisterDrawHandler()

    # helper functions

    def log(self, text, level={'INFO'}):
        self.report(level, text)

    @classmethod
    def poll(cls, context):
        # if context.active_object.mode != 'EDIT':
        #     popover("you must be in edit mode")
        #     return False
        if context.area.type != 'VIEW_3D':
            popover("please invoke from VIEW_3D")
            return False
        return True

    def invoke(self, context, event):
        # args that get passed to draw handler
        args = (self, context)
        # create a draw handler
        self._handle = bpy.types.SpaceView3D.draw_handler_add(  # https://docs.blender.org/api/current/bpy.types.Space.html#bpy.types.Space.draw_handler_add
            draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        # begin modal operator
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancelModal(self):
        self.log("Cancelled...")
        self.unregisterDrawHandler()  # TODO
        return {'CANCELLED'}

    def finishModal(self):
        self.log("Finished...")
        self.unregisterDrawHandler()  # TODO
        return {'FINISHED'}

    def runningModal(self):
        return {'RUNNING_MODAL'}

    def unregisterDrawHandler(self):
        handle = getattr(self, "_handle", None)
        if handle is not None:
            self._handle = None
            bpy.types.SpaceView3D.draw_handler_remove(handle, 'WINDOW')

    def modal(self, context, event):
        context.area.tag_redraw()  # redraw screen

        # Escape
        if event.type == 'ESC':  # or context.active_object.mode != 'EDIT':
            return self.cancelModal()
        # Enter
        if event.type in ['RET', 'NUMPAD_ENTER']:
            if self.axis == "":
                popover("Please specify axis: x, y, or z")
                return self.runningModal()
            self.execute(context)
            return self.finishModal()

        # x,y,z
        if event.unicode in ['x', 'y', 'z']:
            self.axis = event.unicode.lower()
            return self.runningModal()
        # +
        if event.unicode == '+':
            self.sign = 1.0
            return self.runningModal()
        # -
        if event.unicode == '-':
            self.sign = -1.0
            return self.runningModal()

        # Ctrl+V Paste is special. It overrides any in-progress input, and executes immediately
        if event.type == 'V' and event.ctrl is True:
            if self.axis is None:
                popover("Please specify axis: x, y, or z")
                return self.runningModal()

            self.user_input = bpy.context.window_manager.clipboard
            self.sign = 1.0

            if not self.validate(context):
                return self.cancelModal()

            self.execute(context)
            return self.finishModal()

        if event.type == 'BACK_SPACE' and event.value == 'PRESS':
            length = len(self.user_input)
            if length > 0:
                self.user_input = self.user_input[:length-1]
            return self.runningModal()

        # skip invalid input
        if not event.unicode.isdigit() and event.unicode not in ['.', '+', '-']:
            return self.runningModal()  # skip invalid input

        self.user_input += event.unicode

        if not self.validate(context):
            return self.cancelModal()

        return self.runningModal()  # skip invalid input

    def validate(self, context):
        try:
            self.parseInput(context)
        except Exception as e:
            self.log(("invalid input: %s: %s" %
                      (e, self.user_input)), level={'ERROR'})
            return False
        return True

    def parseInput(self, context):
        # default is used if not specified in input
        units_default = context.scene.unit_settings.length_unit  # Millimeters, feet, etc
        system = context.scene.unit_settings.system  # IMPERIAL or METRIC

        # TODO: bpy.utils.units.to_value func can do math !?!! e.g. input 2+5-50 works

        # https://docs.blender.org/api/blender_python_api_2_76_2/bpy.utils.units.html#bpy.utils.units.to_value
        return bpy.utils.units.to_value(system, "LENGTH", self.user_input, units_default)

    def executeOnActiveObject(self, context, val):
        loc = context.active_object.location
        loc[self.axisIndex()] = val

    def axisIndex(self):
        m = {'x': 0, 'y': 1, 'z': 2}
        return m[self.axis]


    def executeOnSelectedVertices(self, context, val):
        # load current mesh in edit mode
        me = context.object.data
        bm = bmesh.from_edit_mesh(me)

        # modify
        i = self.axisIndex()
        for v in bm.verts:
            if v.select:
                v.co[i] = val

        # update
        bmesh.update_edit_mesh(me)

        # See: https://blender.stackexchange.com/questions/149518/bmesh-from-edit-mesh-points-to-old-dead-bmesh-after-free
        # bm.free()

    def execute(self, context):
        if self.validate(context):
            val = self.sign * self.parseInput(context)
            self.log("input received for %s-axis: %s" % (self.axis, val))
            print("input received for %s-axis: %s" % (self.axis, val))
        else:
            popover("error validating final input...")
            return {'FINISHED'}

        mode = context.active_object.mode
        if mode == 'OBJECT':
            self.executeOnActiveObject(context, val)
        elif mode == 'EDIT':
            try:
                self.executeOnSelectedVertices(context, val)
            except Exception as e:
                self.unregisterDrawHandler()
                self.log(("edit execution failed: %s" % e), level={'ERROR'})
                # popover("error in execute:" % e)


        # print(context.active_object.data.vertices[0].select) # for edit mode
        # print(context.active_object.location.x) # for object
        # print(bpy.context.active_object.data.vertices.data.vertices[0].co)
        # context.object.active_object is selected object?
        # for v in context.active_object.data.vertices.data.vertices:
        #     if v.select:
        #         t = v.co.x  # / self.unitMultiplier(context)
        #         print("vert.x: %f " % t)  # local setting

        return {'FINISHED'}


# Copied from blender text templates opereator_modal_draw
def draw_callback_px(self, context):
    units = context.scene.unit_settings.length_unit
    axis = "axis unspecified"
    if self.axis is not None:
        axis = self.axis
    sign = ''
    if self.sign < 0:
        sign = '-'

    # 0 is bottom, 1 above, etc...
    line0 = units + " " + axis
    line1 = sign + self.user_input

    font_id = 0  # XXX, need to find out how best to get this.

    # draw some text
    blf.position(font_id, 15, 30, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, line0)

    blf.position(font_id, 15, 60, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, line1)

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)


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


######################################################################
def main():
    if reload_texts():
        # bpy.utils.unregister_class(AbsoulteOperator)
        print("reloaded")
        return

    bpy.utils.register_class(AbsoulteOperator)
    print("registerd...")

    if bpy.ops.object.absolute_operator.poll():
        print("invoking...")
        bpy.ops.object.absolute_operator(
            'INVOKE_DEFAULT')  # calls invoke first


if __name__ == "__main__":
    main()
