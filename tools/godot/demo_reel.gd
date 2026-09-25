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
	# `-- 7` starts at scene 7 (flags set as if the earlier scenes had been played)
	var args := OS.get_cmdline_user_args()
	var first: String = args[0] if args.size() > 0 else "1"
	var started := first == "1"
	if not started:
		await _jump_to(first)
	for s in SCENES:
		if s[0] == first:
			started = true
		if started:
			print("DEMO scene %s: %.0fs" % [s[0], Time.get_ticks_msec() / 1000.0])
			await call(s[1])
	await _wait(5.0)   # the end card
	print("DEMO done")
	quit()


const SCENES := [["1", "_scene_1"], ["2", "_scene_2"], ["3", "_scene_3"], ["4", "_scene_4"], ["5-6", "_scene_5_6"], ["7", "_scene_7"], ["8", "_scene_8"], ["9", "_scene_9"], ["10", "_scene_10"], ["11-12", "_scene_11_12"]]

## Flags a playthrough would have set by the start of each scene, and where it begins.
const STARTS := {
	"2": [["act1_drill_done", "act1_heard_king_coming"], "winterfell_yard", "armoury_door"],
	"3": [["act1_drill_done", "act1_heard_king_coming", "act1_yard_arrived", "act1_talked_rodrik", "act1_winterfell_prepared"], "wolfswood_holdfast", "treeline"],
	"4": [["act1_winterfell_prepared", "act1_briefed_by_hune", "act1_ring_formed", "act1_deserter_executed"], "kingsroad_north", "bridge"],
	"5-6": [["act1_deserter_executed", "act1_road_arrived", "act1_saw_direwolf", "act1_found_pups"], "winterfell_yard_arrival", "honour_guard_left"],
	"7": [["act1_found_pups", "act1_king_arrived", "act1_arrival_done", "act1_crypts", "act1_crypts_done"], "winterfell_great_hall", "lower_bench"],
	"8": [["act1_crypts", "act1_entered_feast"], "winterfell_yard_visit", "training_yard_gate"],
	"9": [["act1_entered_feast", "act1_visit_arrived", "act1_talked_robb_yard", "act1_explored_during_visit", "act1_visit_done"], "winterfell_yard_fall", "armoury_door"],
	"10": [["act1_explored_during_visit", "act1_bran_fell", "act1_torren_carried_bran", "act1_fall_done"], "winterfell_godswood", "yard_gate"],
	"11-12": [["act1_bran_fell", "act1_aftermath", "act1_godswood", "act1_godswood_done", "act1_recalled"], "winterfell_yard_departure", "gate"],
}


func _jump_to(scene: String) -> void:
	var s: Array = STARTS[scene]
	for f in s[0]:
		GM.set_flag(f)
	if DS.is_running:
		DS._finish()
	SD.goto_level(s[1], s[2])
	await _wait(0.2)


func _npc(who: String) -> Vector2:
	return (root.find_child(who, true, false) as Node2D).global_position


## 1. Morning Duties
func _scene_1() -> void:
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


## 2. Preparing for a King
func _scene_2() -> void:
	await _read_all()
	await _walk_to(Vector2(-200, 60), 3.0, true)
	await _walk_to(_npc("Rodrik") + Vector2(0, 28), 4.0, true)
	player.facing = Vector2.UP
	await _talk()
	await _read_all(3)
	await _walk_to(Vector2(-200, 150), 4.0, true)   # past Hodor
	var hodor := root.find_child("Hodor", true, false) as Node2D
	await _walk_to(hodor.global_position + Vector2(0, 30), 2.0)
	await _talk()
	await _read_all()
	await _walk_to(Vector2(470, 6), 6.0, true)      # the stable doors
	player.facing = Vector2.UP
	await _talk()
	await _read_all()
	await _walk_to(Vector2(0, 300), 6.0, true)
	await _walk_dir("move_down", 1.2)
	await _until_level("wolfswood_holdfast")


## 3. A Deserter's Head
func _scene_3() -> void:
	await _read_all(3)
	await _walk_to(Vector2(-330, 120), 4.0)
	await _walk_to(Vector2(-190, 6), 4.0)
	player.facing = Vector2.UP
	await _talk()
	await _read_all(99, 1.6)   # the sentence: slower, the camera on Bran
	await _wait(1.5)
	await _walk_to(Vector2(200, -48), 6.0, true)
	await _walk_to(Vector2(600, -48), 5.0, true)
	await _until_level("kingsroad_north")


## 4. Six Pups and a Seventh
func _scene_4() -> void:
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
	await _walk_to(Vector2(-85, -428), 4.0, true)   # into the exit at the head of the road
	await _until_level("winterfell_yard_arrival")


## 5-6. The King Comes North, Torchlight (scripted)
func _scene_5_6() -> void:
	await _play_scripted("winterfell_yard_arrival")
	await _play_scripted("winterfell_crypts")


## 7. The Feast
func _scene_7() -> void:
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


## 8. Days of Feasting
func _scene_8() -> void:
	await _read_all()
	var robb := root.find_child("Robb", true, false) as Node2D
	await _walk_to(robb.global_position + Vector2(0, 30), 6.0, true)
	player.facing = Vector2.UP
	await _talk()
	await _play_scripted("winterfell_yard_visit")


## 9. The Fall
func _scene_9() -> void:
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


## 10. Aftermath
func _scene_10() -> void:
	await _until_level("winterfell_godswood")
	await _read_all(3)
	await _walk_to(Vector2(0, 150), 4.0)
	await _walk_to(Vector2(0, -20), 4.0)           # the heart tree
	await _play_scripted("winterfell_godswood", 1.4)


## 11-12. The Departure, Winter Is Coming (scripted)
func _scene_11_12() -> void:
	await _play_scripted("winterfell_yard_departure")
	await _until_level("winterfell_walls")
	for i in 400:
		if DS.is_running:
			await _read_line(1.3)
		elif GM.has_flag("act1_walls_done"):
			break
		await _wait(0.1)


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
	while is_instance_valid(player) and t < timeout and player.global_position.distance_to(target) > 6.0:
		if DS.is_running:   # something to read on the way (a zone, a line)
			_release_all()
			await _read_all()
			if run:
				Input.action_press("run")
		_steer(target)
		await _wait(1.0 / 30.0)
		t += 1.0 / 30.0
		if not is_instance_valid(player):   # walked into an exit: the level has gone
			break
		stuck = stuck + 1.0 / 30.0 if player.global_position.distance_to(last) < 0.5 else 0.0
		last = player.global_position
		if stuck > 0.6:
			break
	_release_all()
	if is_instance_valid(player) and player.global_position.distance_to(target) > 24.0 and not SD.is_transitioning:
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
	for i in 1200:
		if SD.current_level == level and not SD.is_transitioning:
			break
		if i == 1199:
			print("DEMO stuck waiting for ", level, " in ", SD.current_level, " dialogue=",
				DS._current_id if DS.is_running else "-", " flags=", GM.flags.keys())
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
