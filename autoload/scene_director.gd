extends Node
## The only code path that changes what is on screen.
##
## Owns level transitions, act boundaries and cutscene sequencing. Levels are
## instanced into Main/World and freed on transition, which is why autoload
## state is the single source of truth for anything that must survive one.

signal level_changed(level_id: String)
signal act_card_shown(act_id: String)
signal transition_finished()

const LEVEL_DIR := "res://scenes/world/"
const FADE_TIME := 0.4

var current_level: String = ""
var current_spawn: String = ""
var is_transitioning: bool = false

var world_root: Node2D = null          ## set by Main on _ready
var transition_layer: ColorRect = null ## the fade ColorRect, set by Main on _ready


func goto_level(level_id: String, spawn: String = "") -> void:
	if level_id == "" or is_transitioning:
		return
	is_transitioning = true

	await _fade_out()

	if world_root != null:
		for child in world_root.get_children():
			child.queue_free()
		# Freeing is deferred; wait a frame so the old level is gone before the
		# new one is added and both briefly y-sort against each other.
		await get_tree().process_frame

	var path := LEVEL_DIR + level_id + ".tscn"
	if not ResourceLoader.exists(path):
		push_error("SceneDirector: no level scene at %s" % path)
		is_transitioning = false
		return

	var level := (load(path) as PackedScene).instantiate()
	world_root.add_child(level)
	current_level = level_id
	current_spawn = spawn
	_place_player(level, spawn)

	level_changed.emit(level_id)
	_play_level_music(level_id)
	await _fade_in()
	is_transitioning = false
	transition_finished.emit()
	SaveSystem.autosave()


func _place_player(level: Node, spawn: String) -> void:
	if spawn == "":
		return
	var marker := level.find_child(spawn, true, false)
	var player := level.find_child("Player", true, false)
	if marker is Marker2D and player is Node2D:
		player.global_position = (marker as Marker2D).global_position
	elif marker == null:
		push_warning("SceneDirector: no spawn marker %s in %s" % [spawn, current_level])


## Act boundaries show a card, set the POV, start that act's quests and force an
## autosave before the first scene runs.
func begin_act(act_id: String) -> void:
	var act := DialogueSystem.get_act(act_id)
	if act.is_empty():
		return
	if not GameManager.check_flags(act.get("entry_flags", [])):
		push_warning("SceneDirector: entry flags not met for %s" % act_id)

	GameManager.set_act(act_id, String(act.get("pov", "")))
	QuestSystem.start_act_quests(act_id)
	act_card_shown.emit(act_id)

	var scenes: Array = act.get("scenes", [])
	if scenes.is_empty():
		return
	var first: Dictionary = scenes[0]
	await goto_level(String(first.get("level", "")), String(first.get("spawn", "")))
	# A scene with "autostart": false is played, not watched: its dialogue is
	# started by the level (an NPC's dialogue_rules, a trigger) once the player
	# has done what it asks. Act 1's opening drill works this way.
	if bool(first.get("autostart", true)):
		DialogueSystem.start_scene(act_id, String(first["scene_id"]))


## The music bed of the scene now playing out on this level: the latest scene in the
## act that takes place here and whose requires_flags are met (the castle yard is
## scene 2's before the pups are found and scene 5's after). Dialogue nodes can
## override it with their own "music" key - see DialogueSystem._goto().
func _play_level_music(level_id: String) -> void:
	if GameManager.current_act == "":
		return
	var track := ""
	for scene in DialogueSystem.get_act(GameManager.current_act).get("scenes", []):
		if scene.get("level") == level_id and GameManager.check_flags(scene.get("requires_flags", [])):
			track = String(scene.get("music", ""))
	if track != "":
		AudioManager.play_music(track)


## Enters a scene's graph part-way, for trigger volumes and the wave director.
func play_scene(scene_id: String, from_node: String = "") -> void:
	DialogueSystem.start_scene(GameManager.current_act, scene_id, from_node)


func _fade_out() -> void:
	if transition_layer == null:
		return
	var tween := create_tween()
	tween.tween_property(transition_layer, "modulate:a", 1.0, FADE_TIME)
	await tween.finished


func _fade_in() -> void:
	if transition_layer == null:
		return
	var tween := create_tween()
	tween.tween_property(transition_layer, "modulate:a", 0.0, FADE_TIME)
	await tween.finished
