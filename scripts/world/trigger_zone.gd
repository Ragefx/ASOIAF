extends Area2D
## Plays a line of a scene when the player walks into it - finding something rather
## than being told about it (the dead direwolf across the road, the white pup in the
## trees). Once per playthrough: `done_flag` is set by the dialogue node itself, and the
## zone stays quiet once it is.

@export var scene_id: String = ""
@export var node: String = ""
@export var requires_flags: Array[String] = []
@export var done_flag: String = ""


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node) -> void:
	if not body.is_in_group("player") or DialogueSystem.is_running:
		return
	if done_flag != "" and GameManager.has_flag(done_flag):
		return
	if GameManager.check_flags(requires_flags):
		SceneDirector.play_scene(scene_id, node)
