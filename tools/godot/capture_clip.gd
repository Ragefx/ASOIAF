extends SceneTree
## Records a short clip of the game as PNG frames, for previews:
##   godot --path . --resolution 1920x1080 -s tools/godot/capture_clip.gd -- <dir> [frames] [interval] [warmup]
## Frames are the game viewport (the picture before it is scaled to the screen).

func _initialize() -> void:
	change_scene_to_file("res://scenes/Main.tscn")
	_run.call_deferred()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var out := args[0] if args.size() > 0 else "user://clip"
	var n := int(args[1]) if args.size() > 1 else 40
	var dt := float(args[2]) if args.size() > 2 else 0.1
	var warm := float(args[3]) if args.size() > 3 else 3.0
	DirAccess.make_dir_recursive_absolute(out)
	await create_timer(warm).timeout
	for i in n:
		await process_frame
		root.get_texture().get_image().save_png("%s/f%03d.png" % [out, i])
		await create_timer(dt).timeout
	quit()
