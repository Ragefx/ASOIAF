extends Node
## A scripted run of beats - the king's arrival, the fall, the departure - written as data
## in the level instead of as code. Each step is a Dictionary with one key naming what
## it does:
##
##   {"play": "n10"}                 play that node of `scene_id`; wait for it to end
##   {"wait": 1.5}                   seconds
##   {"await_flag": "act1_x"}        wait until the flag is set (by the player, a zone, ...)
##   {"flag": "act1_x"}              set a flag
##   {"lock": true}                  lock / unlock the player's input
##   {"look": "res://....tres"}      dress the player in other SpriteFrames (kneeling, ...)
##   {"show": "group"} / {"hide": "group"}   show or hide every node in a group
##   {"focus": NodePath, "time": 1.2}  glide the camera to a node ({"focus": ""} = back)
##   {"move": NodePath, "to": Vector2, "time": 2.0}  walk a node to a level position
##   {"place_player": Vector2}       put the player there (between two beats, under a fade)
##   {"fade": true} / {"fade": false}  fade to black / back
##   {"zoom": 0.5, "time": 6.0}      ease the camera out (the act's last shot)
##   {"goto": "level", "spawn": "marker"}   move on to the next level
##   {"card": "text"}                end-of-the-built-game card, as the exits show
##
## Runs once the level has faded in, if `requires_flags` are met and `done_flag` is not
## set; `done_flag` is set when it finishes, so a saved game never replays it.

@export var scene_id: String = ""
@export var requires_flags: Array[String] = []
@export var done_flag: String = ""
@export var steps: Array[Dictionary] = []

var _shot: Camera2D = null


func _ready() -> void:
	if done_flag != "" and GameManager.has_flag(done_flag):
		return
	if not GameManager.check_flags(requires_flags):
		return
	if SceneDirector.is_transitioning:
		await SceneDirector.transition_finished
	await get_tree().create_timer(0.3).timeout
	for step in steps:
		if not is_inside_tree():
			return
		await _run(step)
	if done_flag != "":
		GameManager.set_flag(done_flag)


func _player() -> Node2D:
	return get_tree().get_first_node_in_group("player") as Node2D


func _run(step: Dictionary) -> void:
	if step.has("play"):
		SceneDirector.play_scene(scene_id, String(step["play"]))
		if DialogueSystem.is_running:
			await DialogueSystem.dialogue_ended
	elif step.has("wait"):
		await get_tree().create_timer(float(step["wait"])).timeout
	elif step.has("await_flag"):
		while not GameManager.has_flag(String(step["await_flag"])):
			await GameManager.flag_changed
		if DialogueSystem.is_running:
			await DialogueSystem.dialogue_ended
	elif step.has("flag"):
		GameManager.set_flag(String(step["flag"]))
	elif step.has("lock"):
		var p := _player()
		if p != null and p.has_method("set_input_locked"):
			p.set_input_locked(bool(step["lock"]))
	elif step.has("look"):
		var p := _player()
		var spr := p.get_node_or_null("AnimatedSprite2D") as AnimatedSprite2D if p else null
		if spr != null and ResourceLoader.exists(String(step["look"])):
			spr.sprite_frames = load(String(step["look"]))
			var cell := spr.sprite_frames.get_frame_texture(spr.sprite_frames.get_animation_names()[0], 0).get_height()
			spr.offset.y = -cell / 2.0 + 2.0
			spr.play(spr.sprite_frames.get_animation_names()[0])
	elif step.has("show") or step.has("hide"):
		var show := step.has("show")
		for n in get_tree().get_nodes_in_group(String(step["show"] if show else step["hide"])):
			(n as CanvasItem).visible = show
	elif step.has("focus"):
		await _focus(String(step["focus"]), float(step.get("time", 1.2)))
	elif step.has("move"):
		var n := get_node_or_null(NodePath(String(step["move"]))) as Node2D
		if n != null:
			var t := create_tween()
			t.tween_property(n, "global_position", step["to"], float(step.get("time", 2.0)))
			if bool(step.get("wait_for_it", true)):
				await t.finished
	elif step.has("place_player"):
		var p := _player()
		if p != null:
			p.global_position = step["place_player"]
			var cam := p.get_node_or_null("Camera2D") as Camera2D
			if cam != null:
				cam.reset_smoothing()
	elif step.has("fade"):
		await _fade(bool(step["fade"]))
	elif step.has("zoom"):
		var cam := get_viewport().get_camera_2d()
		if cam != null:
			var z := float(step["zoom"])
			await create_tween().set_trans(Tween.TRANS_SINE).tween_property(cam, "zoom", Vector2(z, z), float(step.get("time", 6.0))).finished
	elif step.has("goto"):
		SceneDirector.goto_level(String(step["goto"]), String(step.get("spawn", "")))
	elif step.has("card"):
		_card(String(step["card"]))


## Glide a camera of our own to the node (keeping the level's camera limits), or back
## to the player's camera with an empty path.
func _focus(path: String, time: float) -> void:
	var p := _player()
	var cam := p.get_node_or_null("Camera2D") as Camera2D if p else null
	if cam == null:
		return
	if path == "":
		if _shot == null:
			return
		await create_tween().set_trans(Tween.TRANS_SINE).tween_property(_shot, "global_position", cam.get_screen_center_position(), time).finished
		cam.make_current()
		_shot.queue_free()
		_shot = null
		return
	var target := get_node_or_null(NodePath(path)) as Node2D
	if target == null:
		return
	if _shot == null:
		_shot = Camera2D.new()
		for side in ["limit_left", "limit_top", "limit_right", "limit_bottom"]:
			_shot.set(side, cam.get(side))
		get_parent().add_child(_shot)
		_shot.global_position = cam.get_screen_center_position()
		_shot.make_current()
	await create_tween().set_trans(Tween.TRANS_SINE).tween_property(_shot, "global_position", target.global_position + Vector2(0, -20), time).finished


func _fade(out: bool) -> void:
	var fade := SceneDirector.transition_layer
	if fade == null:
		return
	await create_tween().tween_property(fade, "modulate:a", 1.0 if out else 0.0, 0.6).finished


func _card(text: String) -> void:
	var layer := CanvasLayer.new()
	layer.layer = 50
	var shade := ColorRect.new()
	shade.color = Color(0, 0, 0, 0)
	shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var label := Label.new()
	label.text = text
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.set_anchors_preset(Control.PRESET_FULL_RECT)
	label.modulate.a = 0.0
	layer.add_child(shade)
	layer.add_child(label)
	get_tree().root.add_child(layer)
	var t := layer.create_tween()
	t.tween_property(shade, "color:a", 0.9, 1.5)
	t.parallel().tween_property(label, "modulate:a", 1.0, 2.0)
