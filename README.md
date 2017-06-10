# blendertools


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
