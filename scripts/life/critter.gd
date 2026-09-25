extends AnimatedSprite2D
## A small animal that lives in the level: plays its idle, now and then potters to
## a nearby spot, and bolts when the player comes close. `flees_by` decides how:
## "run" scurries away and settles again, "fly" lifts off and leaves for good.
## Sprites are drawn facing right; flip_h turns them to face their way.

@export var wander_radius: float = 40.0
@export var wander_speed: float = 22.0
@export var flee_radius: float = 70.0
@export_enum("run", "fly", "none") var flees_by: String = "run"
@export var pause_range: Vector2 = Vector2(2.0, 6.0)

var _home: Vector2
var _busy := false
var _gone := false


func _ready() -> void:
	_home = position
	play("idle")
	frame = randi() % maxi(1, sprite_frames.get_frame_count("idle"))
	speed_scale = randf_range(0.85, 1.15)
	flip_h = randf() < 0.5
	_wander_later()


func _process(_delta: float) -> void:
	if _gone or flees_by == "none":
		return
	var player := get_tree().get_first_node_in_group("player") as Node2D
	if player != null and global_position.distance_to(player.global_position) < flee_radius:
		_flee(player.global_position)


func _wander_later() -> void:
	await get_tree().create_timer(randf_range(pause_range.x, pause_range.y)).timeout
	if _gone or not is_inside_tree():
		return
	if not _busy:
		var target := _home + Vector2(randf_range(-1, 1), randf_range(-0.5, 0.5)) * wander_radius
		await _move_to(target, wander_speed)
	_wander_later()


func _move_to(target: Vector2, speed: float) -> void:
	_busy = true
	flip_h = target.x < position.x
	var t := create_tween()
	t.tween_property(self, "position", target, position.distance_to(target) / speed)
	await t.finished
	_busy = false


func _flee(from: Vector2) -> void:
	var away := (global_position - from).normalized()
	if away == Vector2.ZERO:
		away = Vector2.RIGHT
	if flees_by == "fly":
		_gone = true
		flip_h = away.x < 0.0
		var t := create_tween().set_parallel()
		t.tween_property(self, "position", position + away * 260.0 + Vector2(0, -220), 1.6).set_ease(Tween.EASE_IN)
		t.tween_property(self, "modulate:a", 0.0, 1.6)
		await t.finished
		queue_free()
	elif not _busy:
		_home = position + away * 90.0
		await _move_to(_home, wander_speed * 5.0)
