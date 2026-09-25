extends SceneTree
## Walks the Winterfell site (docs/WORLD_DESIGN.md milestone 1) by steering the player
## with the real input actions, and checks the streamed ground keeps up:
##
##   godot --headless --path . -s tools/godot/test_world_site.gd -- --world=winterfell

var failures := 0
var player: CharacterBody2D
var ground: Node


func _initialize() -> void:
	change_scene_to_file("res://scenes/Main.tscn")
	_run.call_deferred()


func _run() -> void:
	var SD := root.get_node("SceneDirector")
	await create_timer(2.0).timeout
	_check(SD.current_level == "winterfell", "--world opens the Winterfell site (%s)" % SD.current_level)
	var level: Node = SD.world_root.get_child(0)
	player = level.find_child("Player", true, false)
	ground = level.find_child("Ground", true, false)
	_check(player != null and ground != null, "the site has a player and streamed ground")
	_check(ground.size_in_cells() == Vector2i(150, 134), "the ground covers the site (%s cells)" % ground.size_in_cells())
	_check(ground.loaded_chunks().size() <= 16, "only chunks near the player are drawn (%d)" % ground.loaded_chunks().size())
	_check(Vector2i(2, 3) in ground.loaded_chunks(), "the chunk under the main gate is drawn")

	# gate -> castle yard -> training yard, straight up the middle
	await _walk("move_up", 7.0, player.global_position + Vector2(0, -1400))
	_check(player.global_position.y < 2300, "walked from the gate up to the training yard (y %.0f)" % player.global_position.y)
	_check(Vector2i(2, 1) in ground.loaded_chunks(), "the ground streamed in ahead (%s)" % str(ground.loaded_chunks()))
	player.global_position = Vector2(2400, 700)
	await create_timer(0.3).timeout
	var far: Array = ground.loaded_chunks().filter(func(c: Vector2i) -> bool: return c.y > 2)
	_check(far.is_empty(), "and cleared once far behind (%s)" % str(far))

	# out through the Hunter's Gate, over the moat bridge
	player.global_position = Vector2(760, 2150)
	await _walk("move_left", 5.0, Vector2(80, 2150))
	_check(player.global_position.x < 180, "out through the Hunter's Gate (x %.0f)" % player.global_position.x)

	# the walls hold: walking north from the training yard stops at the inner wall
	player.global_position = Vector2(3200, 1000)
	await _walk("move_up", 5.0, Vector2(3200, 200))
	_check(player.global_position.y > 560, "the inner wall stops you (y %.0f)" % player.global_position.y)

	# the godswood path reaches the heart tree
	player.global_position = Vector2(1790, 1330)
	await _walk("move_left", 4.0, Vector2(1130, 1330))
	_check(player.global_position.x < 1250, "the godswood path leads to the heart tree (x %.0f)" % player.global_position.x)

	print("SITE %s (%d failure(s))" % ["PASS" if failures == 0 else "FAIL", failures])
	quit(1 if failures else 0)


## Hold a direction until the player is near `goal` or `limit` seconds pass.
func _walk(action: String, limit: float, goal: Vector2) -> void:
	Input.action_press(action)
	Input.action_press("run")
	var t := 0.0
	while t < limit and player.global_position.distance_to(goal) > 40:
		await physics_frame
		t += 1.0 / 60.0
	Input.action_release(action)
	Input.action_release("run")
	await create_timer(0.2).timeout


func _check(ok: bool, what: String) -> void:
	print(("PASS  " if ok else "FAIL  ") + what)
	if not ok:
		failures += 1
