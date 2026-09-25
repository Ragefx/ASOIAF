extends Node2D
## Keeps the player within `radius` of this node - pinned in the honour guard, "cannot
## move more than two tiles". The player can still turn and shuffle; that is the point.

@export var radius: float = 64.0


func _physics_process(_delta: float) -> void:
	var p := get_tree().get_first_node_in_group("player") as Node2D
	if p == null:
		return
	var off := p.global_position - global_position
	if off.length() > radius:
		p.global_position = global_position + off.limit_length(radius)
