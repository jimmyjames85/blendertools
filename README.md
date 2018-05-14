# blendertools

### TODO

	jim@booger  ~  blender
	Read new prefs: /home/jim/.config/blender/2.78/config/userpref.blend
	found bundled python: /opt/blender-2.78b-linux-glibc219-x86_64/2.78/python
	search for unknown operator 'VIEW3D_OT_global_script_runner', 'VIEW3D_OT_global_script_runner'
	search for unknown operator 'VIEW3D_OT_global_script_runner', 'VIEW3D_OT_global_script_runner'
	read blend: /home/jim/git/blendertools/bt/projects/rc_car/blender/rc_car.blend
	search for unknown operator 'VIEW3D_OT_global_script_runner', 'VIEW3D_OT_global_script_runner'



### To import in Blender console

	import sys, importlib
	sys.path.append('/path/to/blendertools')
	import models
	from models.motor_mount.motor_mount import main
	main()
	importlib.reload(btmesh)

	import sys, importlib; sys.path.append('/home/jim/git/blendertools');
	from bt.models.motor_mount.motor_mount import main
	main()
