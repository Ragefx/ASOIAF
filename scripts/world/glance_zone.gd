extends Area2D
## A brief encounter: when the player is within the zone (it rides along on someone
## walking a route) AND facing toward its owner, play the scene line once. Not on
## proximity alone - "if the player's facing intersects her path within two tiles".

@export var scene_id: String = ""
@export var node: String = ""
@export var done_flag: String = ""

var _inside := false


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	body_entered.connect(func(b: Node) -> void: if b.is_in_group("player"): _inside = true)
	body_exited.connect(func(b: Node) -> void: if b.is_in_group("player"): _inside = false)


func _physics_process(_delta: float) -> void:
	if not _inside or DialogueSystem.is_running:
		return
	if done_flag != "" and GameManager.has_flag(done_flag):
		return
	var p := get_tree().get_first_node_in_group("player") as Node2D
	var facing: Vector2 = p.get("facing") if p else Vector2.ZERO
	var to_her := (global_position - p.global_position).normalized()
	if facing.dot(to_her) > 0.5:
		SceneDirector.play_scene(scene_id, node)
