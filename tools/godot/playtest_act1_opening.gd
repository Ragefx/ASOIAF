extends SceneTree
## Automated playthrough of all of Act 1: Morning Duties in the training yard,
## Preparing for a King in the castle yard, A Deserter's Head in the Wolfswood, and Six Pups
## and a Seventh on the kingsroad.
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

	# === Scene 2: Preparing for a King, in the castle yard =========================
	_check(SD.current_level == "winterfell_yard", "the track south leads to the castle yard")
	player = get_first_node_in_group("player")
	await _wait(1.0)
	_check(DS.is_running, "the yard's establishing line plays on arrival")
	await _shot("yard_arrival")
	await _finish_dialogue()
	_check(GM.has_flag("act1_yard_arrived"), "arrival flag set, so it never replays")
	for who in ["Rodrik", "Jory", "StableHand", "Hodor"]:
		var npc := root.find_child(who, true, false)
		var spr := npc.get_node("AnimatedSprite2D") as AnimatedSprite2D if npc else null
		_check(spr != null and spr.sprite_frames != null and spr.is_playing(), "%s is drawn and animated" % who)
	var hodor_h := _sprite_height("Hodor")
	var guard_h := _sprite_height("Rodrik")
	_check(hodor_h > guard_h + 10, "Hodor towers over the grown men (%d px vs Rodrik's %d)" % [hodor_h, guard_h])

	# the stables before orders: a nudge, and nothing changes
	await _interact_at(root.find_child("Stables", true, false) as Node2D, Vector2(0, 16))
	_check(DS.is_running, "the stables answer before Rodrik's orders")
	await _finish_dialogue()
	_check(not GM.has_flag("act1_winterfell_prepared"), "... but can't be finished yet")

	# Jory has nothing for Torren until Rodrik has spoken
	await _talk("Jory")
	_check(not DS.is_running, "Jory waits for Rodrik's orders")

	# Ser Rodrik
	await _talk("Rodrik")
	_check(DS.is_running, "E starts Ser Rodrik's dialogue")
	await _shot("rodrik")
	await _finish_dialogue()
	_check(GM.has_flag("act1_talked_rodrik"), "Rodrik gives his orders")
	await _wait(0.3)
	_check(_hud_text("ObjectiveLabel") == "Make Winterfell ready", "objective advanced to Make Winterfell ready")
	await _talk("Rodrik")
	_check(DS.is_running and DS._current_id == "n14", "Rodrik repeats only 'Stables first. Go.'")
	await _finish_dialogue()

	# the optional three
	await _talk("Jory")
	await _finish_dialogue()
	_check(GM.has_flag("act1_joined_honor_guard"), "Jory puts Torren in the honour guard")
	await _talk("StableHand")
	await _finish_dialogue()
	_check(GM.has_flag("act1_talked_stablehand"), "the stable hand's scene played")
	await _talk("Hodor")
	await _finish_dialogue()
	await _talk("Hodor")
	_check(DS.is_running and DS._current_id == "n42", "Hodor, again: just 'Hodor. Hodor hodor.'")
	await _finish_dialogue()

	# the stables, now with orders: the scene's goal
	await _interact_at(root.find_child("Stables", true, false) as Node2D, Vector2(0, 16))
	await _shot("stables")
	await _finish_dialogue()
	_check(GM.has_flag("act1_winterfell_prepared"), "seeing to the stables readies Winterfell")
	await _wait(0.3)
	_check(_hud_text("ObjectiveLabel") == "Ride out with Lord Stark's party", "objective advanced to Ride out with Lord Stark's party")

	# out the south gate, three days later, into the Wolfswood
	player.global_position = Vector2(0, 320)
	Input.action_press("move_down")
	await _wait(1.0)
	Input.action_release("move_down")
	await _wait(2.5)
	await _shot("yard_exit")

	# === Scene 3: A Deserter's Head, in the Wolfswood ==============================
	_check(SD.current_level == "wolfswood_holdfast", "the south gate leads to the Wolfswood")
	player = get_first_node_in_group("player")
	await _wait(0.8)
	_check(DS.is_running, "the Wolfswood opens on the narrator and Serjeant Hune")
	await _shot("wolfswood_arrival")
	await _finish_dialogue()
	_check(GM.has_flag("act1_briefed_by_hune") and GM.has_flag("act1_ring_formed"), "Hune's briefing forms the ring")
	await _wait(0.3)
	for who in ["Hune", "Eddard", "Bran", "Robb", "Theon", "Jory", "Cley"]:
		var npc := root.find_child(who, true, false)
		var spr := npc.get_node("AnimatedSprite2D") as AnimatedSprite2D if npc else null
		_check(spr != null and spr.sprite_frames != null and spr.is_playing(), "%s is drawn and animated" % who)
	_check(_sprite_height("Bran") < _sprite_height("Robb") and _sprite_height("Robb") < _sprite_height("Eddard"),
		"Bran (%d) < Robb (%d) < Lord Stark (%d)" % [_sprite_height("Bran"), _sprite_height("Robb"), _sprite_height("Eddard")])
	# the four men, before the axe
	for who in [["Jory", "act1_talked_to_jory"], ["Theon", "act1_talked_to_theon"],
			["Robb", "act1_talked_to_robb"], ["Cley", "act1_deserter_cley"]]:
		await _talk(who[0])
		await _finish_dialogue()
		_check(GM.has_flag(who[1]), "spoke with %s" % who[0])
	var gared := root.find_child("prop_001_life_gared", true, false) as CanvasItem
	_check(gared != null and gared.visible, "the deserter kneels in the ring")
	# your place at the left of the ring: the camera goes to Bran, never the block
	var bran := root.find_child("Bran", true, false) as Node2D
	await _interact_at(root.find_child("RingPlace", true, false) as Node2D, Vector2(0, 16))
	_check(DS.is_running, "taking your place starts the sentence")
	await _wait(1.5)
	var view := get_root().get_viewport().get_camera_2d()
	var centre := view.get_screen_center_position()
	_check(centre.distance_to(bran.global_position) < 60.0, "the camera frames Bran (%.0f px off)" % centre.distance_to(bran.global_position))
	await _shot("the_sentence")
	await _finish_dialogue()
	_check(GM.has_flag("act1_deserter_executed"), "the sentence is carried out")
	_check(not gared.visible, "the deserter is gone from the ring")
	await _wait(1.6)
	_check(get_root().get_viewport().get_camera_2d() == player.get_node("Camera2D"), "the camera returns to Torren")
	_check(_hud_text("ObjectiveLabel") == "Ride home", "objective advanced to Ride home")

	# the road home, east
	player.global_position = Vector2(560, -48)
	Input.action_press("move_right")
	await _wait(1.0)
	Input.action_release("move_right")
	await _wait(2.5)
	await _shot("wolfswood_exit")

	# === Scene 4: Six Pups and a Seventh, on the kingsroad ========================
	_check(SD.current_level == "kingsroad_north", "the road east leads onto the kingsroad")
	player = get_first_node_in_group("player")
	await _wait(0.8)
	_check(DS.is_running, "Hune sends Torren up the stopped column")
	await _finish_dialogue()
	_check(GM.has_flag("act1_road_arrived"), "arrival line plays once")
	var jon := root.find_child("Jon", true, false)
	_check(jon != null and (jon.get_node("AnimatedSprite2D") as AnimatedSprite2D).sprite_frames != null, "Jon Snow is drawn")
	# up the road: walking into the party finds her - no button to press
	player.global_position = Vector2(40, -60)
	Input.action_press("move_up")
	await _wait(0.9)
	Input.action_release("move_up")
	await _wait(0.3)
	_check(DS.is_running, "walking up to the party finds the direwolf")
	await _shot("the_direwolf")
	await _finish_dialogue()
	_check(GM.has_flag("act1_saw_direwolf") and GM.has_flag("act1_found_pups"), "the pups are found")
	await _wait(0.3)
	_check(_hud_text("ObjectiveLabel") != "Ride home", "objective moved on from Ride home")
	# the seventh: off the road, in the trees
	_check(not GM.has_flag("act1_found_ghost"), "the white pup is not found by staying on the road")
	player.global_position = Vector2(340, -60)
	Input.action_press("move_right")
	await _wait(0.8)
	Input.action_release("move_right")
	await _wait(0.3)
	_check(DS.is_running, "leaving the road finds the white pup")
	await _shot("the_white_pup")
	await _finish_dialogue()
	_check(GM.has_flag("act1_found_ghost"), "found the white pup")
	# on north, home, a month later: the king comes (up the road's west edge, past the
	# horses and the guard at the head of the column)
	player.global_position = Vector2(-85, -370)
	Input.action_press("move_up")
	await _wait(1.2)
	Input.action_release("move_up")
	await _wait(2.5)

	# === Scene 5: The King Comes North (a scripted beat; Torren held in the line) =====
	_check(SD.current_level == "winterfell_yard_arrival", "the column rides home to the king's arrival")
	player = get_first_node_in_group("player")
	var line_at := player.global_position
	player.global_position = line_at + Vector2(-300, 0)
	await _wait(0.2)
	_check(player.global_position.distance_to(line_at) <= 65.0, "Torren is held in the honour guard line")
	var knelt := false
	var robert_close := false
	for i in 400:
		if DS.is_running:
			if DS._current_id == "n10":
				var spr := player.get_node("AnimatedSprite2D") as AnimatedSprite2D
				knelt = String(spr.sprite_frames.resource_path).contains("torren_kneel")
				var robert := root.find_child("Robert", true, false) as Node2D
				robert_close = robert.global_position.y < 0
				await _shot("the_king")
			await _step_dialogue()
		elif SD.current_level != "winterfell_yard_arrival":
			break
		await _wait(0.1)
	_check(knelt, "the household kneels, and Torren with it, when the king comes")
	_check(robert_close, "the king has walked up the yard to Lord Stark")
	_check(GM.has_flag("act1_king_arrived") and GM.has_flag("act1_met_wells"), "the arrival played through (the king, Ser Emmon)")

	# === Scene 6: Torchlight (the crypts) =============================================
	await _until_level("winterfell_crypts")
	player = get_first_node_in_group("player")
	var torch_ok := String((player.get_node("AnimatedSprite2D") as AnimatedSprite2D).sprite_frames.resource_path).contains("torren_torch")
	_check(torch_ok, "Torren holds a torch at the stair head")
	var start_y := player.global_position.y
	await _play_out("winterfell_crypts", "the_crypts")
	_check(GM.has_flag("act1_heard_crypt_2"), "choosing to listen, twice, hears both fragments")
	_check(GM.has_flag("act1_crypts"), "the crypt scene completes")

	# === Scene 7: The Feast ===========================================================
	await _until_level("winterfell_great_hall")
	player = get_first_node_in_group("player")
	await _wait(0.5)
	await _finish_dialogue()
	_check(GM.has_flag("act1_entered_feast"), "the feast opens")
	for who in [["Hune", "act1_feast_hune"], ["Jory", "act1_feast_jory"], ["Wells", "act1_feast_wells"]]:
		await _talk(who[0])
		await _finish_dialogue()
		_check(GM.has_flag(who[1]), "spoke with %s at the feast" % who[0])
	# the brief encounter: stand in her way, facing her
	var girl := root.find_child("ServingGirl", true, false) as Node2D
	_check(girl != null, "the serving girl crosses the hall")
	for i in 120:
		player.global_position = girl.global_position + Vector2(0, 40)
		player.facing = Vector2.UP
		await _wait(0.05)
		if DS.is_running:
			break
	_check(DS.is_running and GM.has_flag("act1_encounter_feast"), "facing her as she passes: the first brief encounter")
	await _shot("the_feast")
	await _finish_dialogue()
	player.global_position = Vector2(0, 300)
	Input.action_press("move_down")
	await _wait(1.0)
	Input.action_release("move_down")

	# === Scene 8: Days of Feasting ====================================================
	await _until_level("winterfell_yard_visit")
	player = get_first_node_in_group("player")
	await _wait(0.6)
	await _finish_dialogue()
	for who in [["Jon", "act1_talked_to_jon"], ["Tyrion", "act1_met_tyrion"], ["Benjen", "act1_met_benjen"]]:
		await _talk(who[0])
		await _finish_dialogue()
		_check(GM.has_flag(who[1]), "spoke with %s during the visit" % who[0])
	await _shot("the_visit")
	await _talk("Robb")
	await _play_out("winterfell_yard_visit", "")
	_check(GM.has_flag("act1_explored_during_visit"), "nine days pass; the king rides out to hunt")

	# === Scene 9: The Fall ============================================================
	await _until_level("winterfell_yard_fall")
	player = get_first_node_in_group("player")
	await _wait(0.6)
	await _finish_dialogue()
	await _wait(0.4)
	var lances := String((player.get_node("AnimatedSprite2D") as AnimatedSprite2D).sprite_frames.resource_path).contains("torren_lances")
	_check(lances, "Torren carries the lances")
	player.global_position = Vector2(470, -130)   # under the Broken Tower, looking up
	await _wait(0.6)
	_check(DS.is_running, "looking up at the Broken Tower: a small figure on the wall")
	await _shot("the_climber")
	await _finish_dialogue()
	player.global_position = Vector2(0, 150)
	Input.action_press("move_down")
	await _wait(1.2)
	Input.action_release("move_down")
	await _play_out("winterfell_yard_fall", "the_fall")
	_check(GM.has_flag("act1_bran_fell") and GM.has_flag("act1_torren_carried_bran"), "the fall; Torren carries the boy")

	# === Scene 10: Aftermath ==========================================================
	await _until_level("winterfell_godswood")
	player = get_first_node_in_group("player")
	await _wait(0.6)
	await _finish_dialogue()
	_check(GM.has_flag("act1_aftermath"), "the hunting party comes back")
	player.global_position = Vector2(0, 40)
	Input.action_press("move_up")
	await _wait(0.8)
	Input.action_release("move_up")
	await _wait(0.3)
	_check(DS.is_running, "the heart tree")
	await _shot("the_godswood")
	await _play_out("winterfell_godswood", "")

	# === Scenes 11 and 12: the departure and the wall =================================
	await _until_level("winterfell_yard_departure")
	await _wait(0.6)
	for i in 400:
		if DS.is_running:
			if DS._current_id == "n3":
				await _shot("the_departure")
			await _step_dialogue()
		elif SD.current_level != "winterfell_yard_departure":
			break
		await _wait(0.1)
	_check(GM.has_flag("act1_encounter_departure"), "the trunk, and the second brief encounter")
	await _until_level("winterfell_walls")
	await _wait(0.6)
	await _finish_dialogue()
	await _wait(10.0)
	await _shot("winter_is_coming")
	_check(GM.has_flag("act1_complete"), "Act 1 is complete")

	print("PLAYTEST %s (%d failure(s))" % ["PASS" if failures == 0 else "FAIL", failures])
	quit(1 if failures else 0)


func _step_dialogue() -> void:
	if not DS._pending_choices.is_empty():
		DS.choose(0)   # the first choice: in the crypts that is "go one step closer"
	else:
		DS.advance()


func _until_level(level: String) -> void:
	for i in 100:
		if SD.current_level == level and not SD.is_transitioning:
			break
		if DS.is_running:
			await _step_dialogue()
		await _wait(0.1)
	await _wait(0.4)


## Keep answering dialogue (as the player would) until the level changes; shoot once.
func _play_out(level: String, shot: String) -> void:
	var shot_done := shot == ""
	for i in 600:
		if SD.current_level != level:
			return
		if DS.is_running:
			if not shot_done:
				await _shot(shot)
				shot_done = true
			await _step_dialogue()
		await _wait(0.1)


func _finish_dialogue() -> void:
	var steps := 0
	while DS.is_running and steps < 60:
		if not DS._pending_choices.is_empty():
			DS.choose(0)
		else:
			DS.advance()
		steps += 1
		await _wait(0.05)
	await _wait(0.2)


func _interact_at(target: Node2D, offset: Vector2) -> void:
	player.global_position = target.global_position + offset
	player.facing = Vector2.UP
	await _wait(0.4)
	var ev := InputEventAction.new(); ev.action = "interact"; ev.pressed = true
	Input.parse_input_event(ev)
	await _wait(0.5)


func _talk(who: String) -> void:
	await _interact_at(root.find_child(who, true, false) as Node2D, Vector2(0, 28))


## Visible height of an NPC's current frame (the character, not its padded cell).
func _sprite_height(who: String) -> int:
	var spr := root.find_child(who, true, false).get_node("AnimatedSprite2D") as AnimatedSprite2D
	var img := spr.sprite_frames.get_frame_texture(spr.animation, 0).get_image()
	return img.get_used_rect().size.y


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
