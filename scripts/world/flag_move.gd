extends Node
## Moves a node when a flag is set - Torren taking one step closer down the crypt stair
## each time he chooses to listen. Runs as the dialogue goes on, not after it.

@export var target: NodePath
@export var moves: Dictionary = {}   ## flag -> offset (Vector2)
@export var time: float = 0.8


func _ready() -> void:
	GameManager.flag_changed.connect(_on_flag)


func _on_flag(flag: String, value: bool) -> void:
	if not value or not moves.has(flag):
		return
	var n := get_node_or_null(target) as Node2D
	if n == null:
		n = get_tree().get_first_node_in_group("player") as Node2D
	if n != null:
		create_tween().tween_property(n, "global_position", n.global_position + moves[flag], time)
