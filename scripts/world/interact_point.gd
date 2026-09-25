extends Node2D
## Something in the level that isn't a person but can be inspected with E - the
## stables, a door, a grave. The player's InteractArea finds the child Area2D and
## calls interact() here, exactly as it does for an NPC.
##
## Plays `scene_id` from `node` once `requires_flags` are met. `done_flag`, when set,
## makes it go quiet afterwards (the dialogue node itself usually sets that flag).

@export var scene_id: String = ""
@export var node: String = ""
@export var requires_flags: Array[String] = []
@export var done_flag: String = ""
## Said instead while requires_flags aren't met yet ("" = say nothing).
@export var not_yet_node: String = ""
## Optional: while this dialogue runs the camera looks here instead of at the player
## (the deserter's execution frames Bran, never the block).
@export var focus: NodePath
@export var focus_time: float = 1.2


func interact() -> void:
	if DialogueSystem.is_running:
		return
	if done_flag != "" and GameManager.has_flag(done_flag):
		return
	if GameManager.check_flags(requires_flags):
		SceneDirector.play_scene(scene_id, node)
		_look_at_focus()
	elif not_yet_node != "":
		SceneDirector.play_scene(scene_id, not_yet_node)


func _look_at_focus() -> void:
	var target := get_node_or_null(focus) as Node2D
	var player := get_tree().get_first_node_in_group("player") as Node2D
	var cam := player.get_node_or_null("Camera2D") as Camera2D if player else null
	if target == null or cam == null:
		return
	# A camera of our own, with the player camera's limits, glides from where the view
	# is to the focus and back; the player's camera takes over again at the end.
	var shot := Camera2D.new()
	for side in ["limit_left", "limit_top", "limit_right", "limit_bottom"]:
		shot.set(side, cam.get(side))
	get_parent().add_child(shot)
	shot.global_position = cam.get_screen_center_position()
	shot.make_current()
	var t := create_tween().set_trans(Tween.TRANS_SINE)
	t.tween_property(shot, "global_position", target.global_position + Vector2(0, -20), focus_time)
	await DialogueSystem.dialogue_ended
	var back := create_tween().set_trans(Tween.TRANS_SINE)
	back.tween_property(shot, "global_position", cam.get_screen_center_position(), focus_time)
	await back.finished
	cam.make_current()
	shot.queue_free()
