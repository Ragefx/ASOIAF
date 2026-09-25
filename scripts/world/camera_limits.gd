extends Node2D
## Keeps the player's camera inside `rect` (level coordinates), so a walled level
## never shows the void past its edges. A level smaller than the view is centred.

@export var rect: Rect2 = Rect2(-640, -480, 1280, 960)


func _ready() -> void:
	await get_tree().process_frame
	var player := get_tree().get_first_node_in_group("player") as Node2D
	if player == null:
		return
	var cam := player.get_node_or_null("Camera2D") as Camera2D
	if cam == null:
		return
	var r := Rect2(to_global(rect.position), rect.size)
	cam.limit_left = int(r.position.x)
	cam.limit_top = int(r.position.y)
	cam.limit_right = int(r.end.x)
	cam.limit_bottom = int(r.end.y)
