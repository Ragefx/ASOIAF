extends Node
## Plays a line of a scene when the level is entered - a narrator's establishing line,
## say - once per playthrough. Waits for the level's fade-in so the line isn't spoken
## over a black screen.

@export var scene_id: String = ""
@export var node: String = ""
@export var requires_flags: Array[String] = []
@export var once_flag: String = ""  ## set when it has played; it never plays again


func _ready() -> void:
	if once_flag != "" and GameManager.has_flag(once_flag):
		return
	if not GameManager.check_flags(requires_flags):
		return
	if SceneDirector.is_transitioning:
		await SceneDirector.transition_finished
	await get_tree().create_timer(0.3).timeout
	if once_flag != "":
		GameManager.set_flag(once_flag)
	SceneDirector.play_scene(scene_id, node)
