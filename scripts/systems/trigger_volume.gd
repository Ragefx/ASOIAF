class_name TriggerVolume
extends Area2D
## Fires a dialogue node when the player walks into it. Used for the optional
## look-up beats, the brief encounters, and every "the player found this by
## wandering" moment in the chapter.

@export var scene_id: String = ""
@export var node_id: String = ""
@export var requires_flags: Array[String] = []
@export var once: bool = true
@export var goto_level: String = ""      ## set instead of scene_id for a doorway
@export var goto_spawn: String = ""

var _fired: bool = false


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node2D) -> void:
	if not body.is_in_group("player"):
		return
	if (once and _fired) or not GameManager.check_flags(requires_flags):
		return
	_fired = true

	if goto_level != "":
		SceneDirector.goto_level(goto_level, goto_spawn)
	elif scene_id != "":
		DialogueSystem.start_scene(GameManager.current_act, scene_id, node_id)
