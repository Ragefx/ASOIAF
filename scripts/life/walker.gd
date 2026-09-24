extends AnimatedSprite2D
## Someone going about their work: walks back and forth between `points` (relative
## to where it's placed), pausing at each end. Uses "walk_right" flipped for left,
## and "idle" (or the walk's first frame) when stopped.

@export var points: PackedVector2Array = PackedVector2Array([Vector2.ZERO, Vector2(160, 0)])
@export var speed: float = 40.0
@export var pause_range: Vector2 = Vector2(1.5, 4.0)

var _origin: Vector2
var _i := 0


func _ready() -> void:
	_origin = position
	_loop()


func _loop() -> void:
	while is_inside_tree():
		_i = (_i + 1) % points.size()
		var target := _origin + points[_i]
		flip_h = target.x < position.x
		play("walk_right")
		var t := create_tween()
		t.tween_property(self, "position", target, position.distance_to(target) / speed)
		await t.finished
		if sprite_frames.has_animation("idle"):
			play("idle")
		else:
			stop()
			frame = 0
		await get_tree().create_timer(randf_range(pause_range.x, pause_range.y)).timeout
