extends SceneTree
## Walks a world site and saves screenshots (docs/world/shots/) for review:
##
##   godot --path . --resolution 1280x720 -s tools/godot/world_shots.gd -- --world=winterfell
##
## Also checks the streamed ground follows the player and prints the frame time.

var SD: Node
const SPOTS := {
	"gate": Vector2(2400, 3560),
	"castle_yard": Vector2(2700, 3000),
	"training_yard": Vector2(2390, 2000),
	"great_hall": Vector2(2530, 1640),
	"godswood": Vector2(1130, 1330),
	"first_keep": Vector2(3450, 1300),
	"stables": Vector2(3500, 3250),
	"hunters_gate": Vector2(760, 2150),
}


func _initialize() -> void:
	change_scene_to_file("res://scenes/Main.tscn")
	_run.call_deferred()


func _run() -> void:
	SD = root.get_node("SceneDirector")
	await create_timer(3.0).timeout
	var level: Node = SD.world_root.get_child(0) if SD.world_root.get_child_count() else null
	print("WORLD level=%s" % SD.current_level)
	var player := level.find_child("Player", true, false) as Node2D
	var ground: Node = level.find_child("Ground", true, false)
	DirAccess.make_dir_recursive_absolute("res://docs/world/shots")
	for spot in SPOTS:
		player.global_position = SPOTS[spot]
		var cam := player.get_node("Camera2D") as Camera2D
		cam.reset_smoothing()
		var t0 := Time.get_ticks_usec()
		await process_frame
		var t1 := Time.get_ticks_usec()
		await create_timer(0.8).timeout
		var img := root.get_texture().get_image()
		img.save_png("res://docs/world/shots/%s.png" % spot)
		print("WORLD shot %s chunks=%d first_frame=%.1fms fps=%d" % [spot, ground.loaded_chunks().size(), (t1 - t0) / 1000.0, Engine.get_frames_per_second()])
	quit(0)
