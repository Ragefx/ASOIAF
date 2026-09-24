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


func interact() -> void:
	if DialogueSystem.is_running:
		return
	if done_flag != "" and GameManager.has_flag(done_flag):
		return
	if GameManager.check_flags(requires_flags):
		SceneDirector.play_scene(scene_id, node)
	elif not_yet_node != "":
		SceneDirector.play_scene(scene_id, not_yet_node)
