# no need for console any more, use F5 to create new refresh by doing the following:
# https://blender.stackexchange.com/questions/34722/global-keyboard-shortcut-to-execute-text-editor-script
#
# User Preferences -> 3D View -> 3D View (Global) -> Add New
# Name: view3d.f5_reload_it
# Key: F5 (or whatever you like)
#
# Paste the following into the text editor pane and run the script once
#
# Ctrl+Up (or Alt+F10 for fullscreen)
# then F5 to refresh
#
# TODO move this into blenderkeys

import os, bpy, time

km_refresh_f5_name = "view3d.f5_reload_it"
km_refresh_f5_label = "f5 reload it"

class GlobalScriptRunner(bpy.types.Operator):
    """Tooltip"""
    bl_idname = km_refresh_f5_name
    bl_label = km_refresh_f5_label #"Global Script Runner"

    # @classmethod
    # def poll(cls, context):
    #    return context.active_object is not None
    def execute(self, context):
        import sys, importlib;
        sys.path.append('/home/jim/git/blendertools');
        from bt.models.hinge import hinge;
        print('reloading...');
        importlib.reload(hinge);
        print('loaded');
        obj = hinge.main()  # todo does mean obj can be referred to within the blender console?
        print("%f" % (time.time()))
        return {'FINISHED'}


def register():
    bpy.utils.register_class(GlobalScriptRunner)


def unregister():
    bpy.utils.unregister_class(GlobalScriptRunner)


# This comes from File -> User_Pref -> Export_Key_Config
def kmi_props_setattr(kmi_props, attr, value):
    try:
        setattr(kmi_props, attr, value)
    except AttributeError:
        print("Warning: property '%s' not found in keymap item '%s'" %
              (attr, kmi_props.__class__.__name__))
    except Exception as e:
        print("Warning: %r" % e)


if __name__ == "__main__":
    print("new")
    register()

    # F5 hotkey to reload
    # Map 3D View

    bpy.ops.wm.keyconfig_activate(filepath="/home/jim/git/blendertools/blenderkeys/view3d_f5_reload_it.py")


# : D
# bpy.ops.script.python_file_run(filepath="/home/jim/git/blendertools/global_script_runner.py")
#
