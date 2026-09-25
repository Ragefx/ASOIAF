extends SceneTree
## Checks the plumbing around the scenes rather than a playthrough:
##
##   xvfb-run -s "-screen 0 2560x1440x24" godot --path . --resolution 2560x1440 \
##       -s tools/godot/test_systems.gd
##
## Needs a fresh start (no autosave in user://saves); leaves one behind, like a player.
## - each level picks its scene's music bed, and a dialogue line can cut it
## - a level transition autosaves; the autosave restores level, flags and quests
## - Esc pauses; New game (pressed twice) forgets everything and reopens Chapter 1

var failures := 0
var SD: Node
var DS: Node
var GM: Node
var SS: Node
var AM: Node
var QS: Node


func _initialize() -> void:
	change_scene_to_file("res://scenes/Main.tscn")
	_run.call_deferred()


func _run() -> void:
	SD = root.get_node("SceneDirector")
	DS = root.get_node("DialogueSystem")
	GM = root.get_node("GameManager")
	SS = root.get_node("SaveSystem")
	AM = root.get_node("AudioManager")
	QS = root.get_node("QuestSystem")
	await _wait(3.0)
	_check(SD.current_level == "winterfell_training_yard", "fresh start opens the training yard")
	_check(AM.current_track == "winterfell_morning", "training yard plays its scene's bed (%s)" % AM.current_track)

	# --- music by level and by line ---------------------------------------------
	for f in ["act1_drill_done", "act1_heard_king_coming"]:
		GM.set_flag(f)
	await _goto("winterfell_yard", "armoury_door")
	_check(AM.current_track == "winterfell_busy", "castle yard plays Preparing for a King's bed (%s)" % AM.current_track)
	await _end_dialogue()
	for f in ["act1_talked_rodrik", "act1_winterfell_prepared"]:
		GM.set_flag(f)
	await _goto("wolfswood_holdfast", "treeline")
	_check(AM.current_track == "north_cold_open", "the Wolfswood plays its bed (%s)" % AM.current_track)
	await _end_dialogue()
	GM.set_flag("act1_ring_formed")
	DS.start_scene("act_1", "s1_03_the_deserter", "n50")
	_check(AM.current_track == "none", "the sentence is played in silence")
	await _end_dialogue()

	# --- autosave and continue --------------------------------------------------
	_check(SS.has_save(0), "the level transition autosaved")
	var saved: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SS.slot_path(0)))
	_check(saved.get("level") == "wolfswood_holdfast", "the autosave is of the Wolfswood")
	GM.set_flag("act1_test_marker")
	SS.load_game(0)
	await _wait(1.5)
	_check(SD.current_level == "wolfswood_holdfast", "continuing restores the level")
	_check(GM.has_flag("act1_winterfell_prepared") and not GM.has_flag("act1_test_marker"),
		"continuing restores the flags as they were saved")
	_check(QS.active.size() > 0, "continuing restores the quests")
	await _end_dialogue()

	# --- pause and New game -----------------------------------------------------
	var menu := root.find_child("PauseMenu", true, false)
	_check(menu != null, "pause menu present")
	var esc := InputEventAction.new(); esc.action = "ui_cancel"; esc.pressed = true
	Input.parse_input_event(esc)
	await _wait(0.2)
	_check(paused, "Esc pauses the game")
	var new_game := menu.find_child("NewGame", true, false) as Button
	new_game.pressed.emit()
	_check(paused and new_game.text != "New game", "New game asks for confirmation first")
	new_game.pressed.emit()
	await _wait(3.5)
	_check(not paused, "the game runs again")
	_check(SD.current_level == "winterfell_training_yard", "New game reopens the training yard")
	_check(not GM.has_flag("act1_winterfell_prepared") and not GM.has_flag("act1_drill_done"), "New game forgets every flag")
	var obj := root.find_child("ObjectiveLabel", true, false) as Label
	_check(obj != null and obj.text == "Finish your drill", "objective is back to Finish your drill (%s)" % (obj.text if obj else ""))

	print("SYSTEMS %s (%d failure(s))" % ["PASS" if failures == 0 else "FAIL", failures])
	quit(1 if failures else 0)


func _goto(level: String, spawn: String) -> void:
	SD.goto_level(level, spawn)
	await _wait(1.6)


func _end_dialogue() -> void:
	await _wait(0.5)
	var steps := 0
	while DS.is_running and steps < 60:
		if not DS._pending_choices.is_empty():
			DS.choose(0)
		else:
			DS.advance()
		steps += 1
		await _wait(0.03)


func _check(ok: bool, what: String) -> void:
	print(("PASS  " if ok else "FAIL  ") + what)
	if not ok:
		failures += 1


func _wait(t: float) -> void:
	await create_timer(t, true).timeout
