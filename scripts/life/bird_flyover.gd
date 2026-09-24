extends Node2D
## Now and then a bird (or a few) crosses the sky over the view, with a shadow
## sliding across the ground below it. `bird_frames` needs a "fly" animation drawn
## heading right; the shadow is the same frames, darkened and flattened.

@export var bird_frames: SpriteFrames
@export var interval := Vector2(6.0, 14.0)
@export var height := 150.0   ## how far above its shadow the bird flies


func _ready() -> void:
	_loop()


func _loop() -> void:
	while is_inside_tree():
		await get_tree().create_timer(randf_range(interval.x, interval.y)).timeout
		var cam := get_viewport().get_camera_2d()
		if cam == null or bird_frames == null:
			continue
		var n := 1 if randf() < 0.6 else randi_range(2, 4)
		var dir := 1.0 if randf() < 0.5 else -1.0
		var y := cam.global_position.y + randf_range(-250, 200)
		for i in n:
			_fly(cam.global_position, dir, y + randf_range(-30, 30), i * 0.35)


func _fly(center: Vector2, dir: float, y: float, delay: float) -> void:
	await get_tree().create_timer(delay).timeout
	var half := get_viewport_rect().size.x / 2.0 + 120.0
	var start := Vector2(center.x - half * dir, y)
	var end := Vector2(center.x + half * dir, y + randf_range(-80, 80))
	var shadow := AnimatedSprite2D.new()
	var bird := AnimatedSprite2D.new()
	for s in [shadow, bird]:
		s.sprite_frames = bird_frames
		s.play("fly")
		s.flip_h = dir < 0.0
		s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		add_child(s)
	shadow.modulate = Color(0, 0, 0, 0.22)
	shadow.scale = Vector2(1.0, 0.6)
	shadow.z_index = 1
	bird.z_index = 60
	var dur := randf_range(5.0, 8.0)
	var t := create_tween()
	t.tween_method(func(k: float) -> void:
		var p := start.lerp(end, k)
		shadow.global_position = p.round()
		bird.global_position = (p + Vector2(0, -height)).round(), 0.0, 1.0, dur)
	t.tween_callback(shadow.queue_free)
	t.tween_callback(bird.queue_free)
