extends SceneTree
## Automated playthrough of Act 1's opening scene (Morning Duties).
##
##   xvfb-run -s "-screen 0 2560x1440x24" godot --path . --resolution 2560x1440 \
##       -s tools/godot/playtest_act1_opening.gd -- <screenshot_dir>
##
## Needs a fresh start (no autosave in user://saves). Drives the real game through
## Godot's input system and the same calls the UI makes, screenshots each beat, and
## prints PASS/FAIL per check. Exit code 1 if any check failed.

var out_dir := "user://playtest"
var failures := 0
var player: Node2D
var shot_n := 0
# Autoloads aren't compile-time identifiers in a -s script; fetched in _run().
var SD: Node
var DS: Node
var GM: Node


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		out_dir = args[0]
	DirAccess.make_dir_recursive_absolute(out_dir)
	change_scene_to_file("res://scenes/Main.tscn")
	_run.call_deferred()


func _run() -> void:
	SD = root.get_node("SceneDirector")
	DS = root.get_node("DialogueSystem")
	GM = root.get_node("GameManager")
	await _wait(3.0)  # act card + fade-in
	player = get_first_node_in_group("player")
	_check(player != null, "player spawned")
	_check(SD.current_level == "winterfell_training_yard", "opening level loaded")
	_check(not DS.is_running, "no dialogue on arrival (scene starts with the drill)")
	_check(_hud_text("ObjectiveLabel") == "Finish your drill", "objective: Finish your drill")
	await _shot("start")

	# --- movement, through the input map --------------------------------------
	var p0 := player.global_position
	Input.action_press("move_left")
	await _wait(0.5)
	await _shot("walking")
	Input.action_release("move_left")
	_check(player.global_position.x < p0.x - 30.0, "WASD moves the player (moved %.0f px)" % (p0.x - player.global_position.x))
	var anim_ok := String(player.get_node("AnimatedSprite2D").animation).begins_with("walk")
	_check(anim_ok, "walk animation plays while moving")
	await _wait(0.3)

	# --- the drill ---------------------------------------------------------------
	var dummy := _find_drill_dummy()
	_check(dummy != null, "drill dummy present")
	player.global_position = dummy.global_position + Vector2(0, 14)  # where its base collider stops you
	player.facing = Vector2.UP
	await _wait(0.2)
	for i in 5:
		Input.action_press("attack_light")
		var ev := InputEventAction.new(); ev.action = "attack_light"; ev.pressed = true
		Input.parse_input_event(ev)
		await _wait(0.07)
		if i == 1:
			await _shot("swing")
		Input.action_release("attack_light")
		var ev2 := InputEventAction.new(); ev2.action = "attack_light"; ev2.pressed = false
		Input.parse_input_event(ev2)
		await _wait(0.45)
	_check(int(dummy.get("hits")) >= 5, "dummy took %d hits" % int(dummy.get("hits")))
	_check(GM.has_flag("act1_drill_done"), "drill flag set")
	await _wait(0.5)
	_check(_hud_text("ObjectiveLabel") == "Hear Ser Cley's news", "objective advanced to Hear Ser Cley's news")
	await _shot("drill_done")

	# --- Ser Cley ------------------------------------------------------------------
	var cley := root.find_child("Cley", true, false) as Node2D
	_check(cley != null and (cley.get_node("AnimatedSprite2D") as AnimatedSprite2D).sprite_frames != null, "Cley has a sprite")
	player.global_position = cley.global_position + Vector2(0, 28)
	player.facing = Vector2.UP
	await _wait(0.4)
	var ev3 := InputEventAction.new(); ev3.action = "interact"; ev3.pressed = true
	Input.parse_input_event(ev3)
	await _wait(0.6)
	_check(DS.is_running, "E starts Cley's dialogue")
	await _shot("dialogue")
	var steps := 0
	while DS.is_running and steps < 60:
		if not DS._pending_choices.is_empty():
			DS.choose(0)
		else:
			DS.advance()
		steps += 1
		await _wait(0.05)
	_check(not DS.is_running, "dialogue ran to its end (%d steps)" % steps)
	_check(GM.has_flag("act1_heard_arryn_dead") and GM.has_flag("act1_heard_king_coming"), "news flags set")
	await _wait(0.5)
	_check(_hud_text("ObjectiveLabel") == "Report to Ser Rodrik", "objective advanced to Report to Ser Rodrik")
	await _shot("after_news")

	# talking again must not replay the scene
	Input.parse_input_event(ev3)
	await _wait(0.4)
	_check(not DS.is_running, "Cley does not repeat the scene")

	# --- leaving -------------------------------------------------------------------
	player.global_position = Vector2(0, 250)
	Input.action_press("move_down")
	await _wait(1.0)
	Input.action_release("move_down")
	await _wait(2.5)
	await _shot("exit")

	print("PLAYTEST %s (%d failure(s))" % ["PASS" if failures == 0 else "FAIL", failures])
	quit(1 if failures else 0)


func _find_drill_dummy() -> Node2D:
	for n in root.find_children("*", "CharacterBody2D", true, false):
		if n.get("completion_flag") == "act1_drill_done":
			return n
	return null


func _hud_text(label: String) -> String:
	var l := root.find_child(label, true, false) as Label
	return l.text if l != null else ""


func _check(ok: bool, what: String) -> void:
	print(("PASS  " if ok else "FAIL  ") + what)
	if not ok:
		failures += 1


func _wait(t: float) -> void:
	await create_timer(t).timeout


func _shot(name: String) -> void:
	await process_frame
	await process_frame
	shot_n += 1
	var img := root.get_texture().get_image()
	img.save_png("%s/%02d_%s.png" % [out_dir, shot_n, name])
