extends Node2D
## Leaves let go of the trees now and then and drift down, swaying, then settle and
## fade. Picks a random tree near the camera (any node in group "tree") so leaves
## fall where the player can see them. Leaf texture: 2 hframes of tiny leaves.

@export var leaf_texture: Texture2D
@export var interval := Vector2(0.4, 1.4)
@export var near := 700.0


func _ready() -> void:
	_spawn_loop()


func _spawn_loop() -> void:
	while is_inside_tree():
		await get_tree().create_timer(randf_range(interval.x, interval.y)).timeout
		var cam := get_viewport().get_camera_2d()
		if cam == null:
			continue
		var trees := get_tree().get_nodes_in_group("tree").filter(
			func(t: Node) -> bool: return (t as Node2D).global_position.distance_to(cam.global_position) < near)
		if trees.is_empty():
			continue
		_drop((trees.pick_random() as Node2D).global_position + Vector2(randf_range(-40, 40), randf_range(-120, -60)))


func _drop(from: Vector2) -> void:
	var leaf := Sprite2D.new()
	leaf.texture = leaf_texture
	leaf.hframes = 2
	leaf.frame = randi() % 2
	leaf.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	leaf.global_position = from
	leaf.z_index = 40
	add_child(leaf)
	var fall := randf_range(60.0, 110.0)
	var side := randf_range(-50.0, 50.0)
	var t := leaf.create_tween()
	t.tween_method(func(k: float) -> void:
		leaf.global_position = (from + Vector2(side * k + sin(k * 9.0) * 8.0, fall * k)).round()
		leaf.flip_h = cos(k * 9.0) < 0.0, 0.0, 1.0, fall / 28.0)
	t.tween_interval(1.5)
	t.tween_property(leaf, "modulate:a", 0.0, 1.0)
	t.tween_callback(leaf.queue_free)
