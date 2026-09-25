extends SceneTree
## A played-through tour of Act 1 for a video: walks rather than teleports, reads each
## line at a readable pace, and skips the optional talk so it stays short.
##
##   xvfb-run -s "-screen 0 1280x720x24" godot --path . --resolution 1280x720 \
##       --write-movie /tmp/demo.avi --fixed-fps 30 -s tools/godot/demo_reel.gd
##
## 1280x720 is exactly what a 2560x1440 screen shows at the game's 2x pixels, so the
## video is the game's own framing, one video pixel per game pixel. Needs a fresh start
## (no autosave in user://saves). Movie Maker mode runs the game on its own clock, so
## the timings below are game time, not how long the render takes.

var SD: Node
var DS: Node
var GM: Node
var player: Node2D
const READ_AFTER := 1.1      ## seconds a line stays up once fully shown
const QUICK_AFTER := 0.5     ## ... for lines in the middle of long exchanges


func _initialize() -> void:
	change_scene_to_file("res://scenes/Main.tscn")
	_run.call_deferred()


func _run() -> void:
	SD = root.get_node("SceneDirector")
	DS = root.get_node("DialogueSystem")
	GM = root.get_node("GameManager")
	await _wait(3.2)

	# 1. Morning Duties -------------------------------------------------------------
	print("DEMO scene 1: %.0fs" % (Time.get_ticks_msec() / 1000.0))
	_me()
	await _walk_to(Vector2(-60, 30), 1.4)
	await _walk_to(Vector2(0, 30), 0.8)
	var dummy := _find_drill_dummy()
	await _walk_to(dummy.global_position + Vector2(0, 16), 2.0)
	player.facing = Vector2.UP
	for i in 5:
		await _swing()
	await _wait(0.8)
	var cley := root.find_child("Cley", true, false) as Node2D
	await _walk_to(cley.global_position + Vector2(0, 30), 4.0)
	await _talk()
	await _read_all(4)
	await _walk_to(Vector2(0, 240), 5.0, true)
	await _walk_dir("move_down", 1.2)
	await _until_level("winterfell_yard")

	# 2. Preparing for a King -------------------------------------------------------
	print("DEMO scene 2: %.0fs" % (Time.get_ticks_msec() / 1000.0))
	await _read_all()
	await _walk_to(Vector2(-200, 60), 3.0, true)
	await _walk_to(Vector2(-40, -150), 4.0, true)
	player.facing = Vector2.UP
	await _talk()
	await _read_all(3)
	await _walk_to(Vector2(-200, 150), 4.0, true)   # past Hodor
	var hodor := root.find_child("Hodor", true, false) as Node2D
	await _walk_to(hodor.global_position + Vector2(0, 30), 2.0)
	await _talk()
	await _read_all()
	await _walk_to(Vector2(470, 10), 6.0, true)
	player.facing = Vector2.UP
	await _talk()
	await _read_all()
	await _walk_to(Vector2(0, 300), 6.0, true)
	await _walk_dir("move_down", 1.2)
	await _until_level("wolfswood_holdfast")

	# 3. A Deserter's Head ----------------------------------------------------------
	print("DEMO scene 3: %.0fs" % (Time.get_ticks_msec() / 1000.0))
	await _read_all(3)
	await _walk_to(Vector2(-330, 120), 4.0)
	await _walk_to(Vector2(-190, 10), 4.0)
	player.facing = Vector2.UP
	await _talk()
	await _read_all(99, 1.6)   # the sentence: slower, the camera on Bran
	await _wait(1.5)
	await _walk_to(Vector2(200, -48), 6.0, true)
	await _walk_to(Vector2(600, -48), 5.0, true)
	await _until_level("kingsroad_north")

	# 4. Six Pups and a Seventh -----------------------------------------------------
	print("DEMO scene 4: %.0fs" % (Time.get_ticks_msec() / 1000.0))
	await _read_all()
	await _walk_to(Vector2(40, 100), 4.0, true)
	await _walk_to(Vector2(40, -120), 4.0)        # walking into the party finds her
	await _read_all(3)
	await _wait(1.0)
	await _walk_to(Vector2(200, -60), 3.0, true)
	await _walk_to(Vector2(400, -60), 3.0)        # off the road: the white pup
	await _read_all(99, 1.8)
	await _walk_to(Vector2(40, -200), 5.0, true)
	await _walk_to(Vector2(-85, -300), 4.0, true)
	await _walk_dir("move_up", 1.5)
	await _until_level("winterfell_yard_arrival")

	# 5-6. The King Comes North, Torchlight (scripted) ------------------------------
	print("DEMO scene 5-6: %.0fs" % (Time.get_ticks_msec() / 1000.0))
	await _play_scripted("winterfell_yard_arrival")
	await _play_scripted("winterfell_crypts")

	# 7. The Feast -------------------------------------------------------------------
	print("DEMO scene 7: %.0fs" % (Time.get_ticks_msec() / 1000.0))
	await _until_level("winterfell_great_hall")
	await _read_all()
	await _walk_to(Vector2(-150, 200), 3.0)
	var girl := root.find_child("ServingGirl", true, false) as Node2D
	for i in 300:   # step into her path as she comes, and look at her
		var ahead := girl.global_position + Vector2(0, 44)
		if player.global_position.distance_to(ahead) > 8.0:
			_steer(ahead)
		else:
			_release_all()
			player.facing = Vector2.UP
		await _wait(1.0 / 30.0)
		if DS.is_running:
			break
	_release_all()
	await _read_all(99, 1.4)
	await _walk_to(Vector2(0, 250), 5.0, true)
	await _walk_dir("move_down", 1.2)
	await _until_level("winterfell_yard_visit")

	# 8. Days of Feasting ------------------------------------------------------------
	print("DEMO scene 8: %.0fs" % (Time.get_ticks_msec() / 1000.0))
	await _read_all()
	var robb := root.find_child("Robb", true, false) as Node2D
	await _walk_to(robb.global_position + Vector2(0, 30), 6.0, true)
	player.facing = Vector2.UP
	await _talk()
	await _play_scripted("winterfell_yard_visit")

	# 9. The Fall ----------------------------------------------------------------------
	print("DEMO scene 9: %.0fs" % (Time.get_ticks_msec() / 1000.0))
	await _until_level("winterfell_yard_fall")
	await _read_all()
	await _wait(0.5)
	await _walk_to(Vector2(-200, 60), 3.0)
	await _walk_to(Vector2(300, -60), 5.0)
	await _walk_to(Vector2(470, -130), 3.0)        # under the Broken Tower, looking up
	await _read_all(99, 1.6)
	await _walk_to(Vector2(200, 120), 4.0)
	await _walk_to(Vector2(0, 230), 4.0)           # the lances to the gate, and behind him...
	await _play_scripted("winterfell_yard_fall", 1.4)

	# 10. Aftermath --------------------------------------------------------------------
	print("DEMO scene 10: %.0fs" % (Time.get_ticks_msec() / 1000.0))
	await _until_level("winterfell_godswood")
	await _read_all(3)
	await _walk_to(Vector2(0, 150), 4.0)
	await _walk_to(Vector2(0, 20), 4.0)            # the heart tree
	await _play_scripted("winterfell_godswood", 1.4)

	# 11-12. The Departure, Winter Is Coming (scripted) ------------------------------
	print("DEMO scene 11-12: %.0fs" % (Time.get_ticks_msec() / 1000.0))
	await _play_scripted("winterfell_yard_departure")
	await _until_level("winterfell_walls")
	for i in 400:
		if DS.is_running:
			await _read_line(1.3)
		elif GM.has_flag("act1_walls_done"):
			break
		await _wait(0.1)
	await _wait(5.0)   # the end card
	print("DEMO done")
	quit()


# --- movement ------------------------------------------------------------------------

func _me() -> void:
	for p in get_nodes_in_group("player"):
		if not p.is_queued_for_deletion() and p.is_inside_tree():
			player = p
			return


const DIRS := {"move_left": Vector2.LEFT, "move_right": Vector2.RIGHT, "move_up": Vector2.UP, "move_down": Vector2.DOWN}


func _steer(target: Vector2) -> void:
	var d := target - player.global_position
	for a in DIRS:
		var along: float = d.dot(DIRS[a])
		if along > 4.0:
			Input.action_press(a)
		else:
			Input.action_release(a)


func _release_all() -> void:
	for a in DIRS:
		Input.action_release(a)
	Input.action_release("run")


## Walk (or run) toward a point; give up after `timeout` seconds of game time, and if
## blocked, cut to it - a demo shouldn't show someone walking into a barrel for a minute.
func _walk_to(target: Vector2, timeout: float, run := false) -> void:
	_me()
	if run:
		Input.action_press("run")
	var t := 0.0
	var last := player.global_position
	var stuck := 0.0
	while t < timeout and player.global_position.distance_to(target) > 6.0:
		if DS.is_running:   # something to read on the way (a zone, a line)
			_release_all()
			await _read_all()
			if run:
				Input.action_press("run")
		_steer(target)
		await _wait(1.0 / 30.0)
		t += 1.0 / 30.0
		stuck = stuck + 1.0 / 30.0 if player.global_position.distance_to(last) < 0.5 else 0.0
		last = player.global_position
		if stuck > 0.6:
			break
	_release_all()
	if player.global_position.distance_to(target) > 24.0 and not SD.is_transitioning:
		player.global_position = target


func _walk_dir(action: String, time: float) -> void:
	Input.action_press(action)
	await _wait(time)
	Input.action_release(action)


func _swing() -> void:
	var ev := InputEventAction.new()
	ev.action = "attack_light"
	ev.pressed = true
	Input.parse_input_event(ev)
	await _wait(0.1)
	var up := InputEventAction.new()
	up.action = "attack_light"
	up.pressed = false
	Input.parse_input_event(up)
	await _wait(0.45)


func _talk() -> void:
	await _wait(0.2)
	var ev := InputEventAction.new()
	ev.action = "interact"
	ev.pressed = true
	Input.parse_input_event(ev)
	await _wait(0.4)


# --- reading -------------------------------------------------------------------------

## Wait for the typewriter to finish, hold, then answer (first choice) or advance.
func _read_line(hold := READ_AFTER) -> void:
	var ui := root.find_child("DialogueUI", true, false)
	for i in 400:
		var shown: float = ui.get("_revealed")
		var full: String = ui.get("_full_text")
		if shown >= full.length():
			break
		await _wait(0.05)
	await _wait(hold)
	if not DS.is_running:
		return
	if not DS._pending_choices.is_empty():
		await _wait(0.6)   # let the choices be seen
		DS.choose(0)
	else:
		DS.advance()
	await _wait(0.15)


## Read a whole exchange: the first `slow` lines at full pace, the rest quicker.
func _read_all(slow := 2, hold := READ_AFTER) -> void:
	await _wait(0.3)
	var n := 0
	while DS.is_running:
		await _read_line(hold if n < slow else QUICK_AFTER)
		n += 1


## A scripted scene: just read along until the level changes.
func _play_scripted(level: String, hold := READ_AFTER) -> void:
	await _until_level(level)
	for i in 3000:
		if SD.current_level != level:
			return
		if DS.is_running:
			await _read_line(hold)
		await _wait(0.05)


func _until_level(level: String) -> void:
	for i in 400:
		if SD.current_level == level and not SD.is_transitioning:
			break
		if DS.is_running:
			await _read_line(QUICK_AFTER)
		await _wait(0.1)
	await _wait(0.5)
	_me()


func _find_drill_dummy() -> Node2D:
	for n in root.find_children("*", "CharacterBody2D", true, false):
		if n.get("completion_flag") == "act1_drill_done":
			return n
	return null


func _wait(t: float) -> void:
	await create_timer(t).timeout
