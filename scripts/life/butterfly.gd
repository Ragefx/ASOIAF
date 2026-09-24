extends Sprite2D
## A butterfly: two-frame flap (hframes = 2), fluttering in loose loops around
## where it was placed, drifting between flowers. Purely decorative.

@export var roam: float = 60.0

var _home: Vector2
var _t := 0.0
var _flap := 0.0
var _seed := 0.0


func _ready() -> void:
	_home = position
	_seed = randf() * 100.0
	_t = randf() * 10.0


func _process(delta: float) -> void:
	_t += delta
	_flap += delta
	if _flap > 0.09:
		_flap = 0.0
		frame = 1 - frame
	var p := Vector2(
		sin(_t * 0.7 + _seed) * roam + sin(_t * 2.3 + _seed * 2.0) * 10.0,
		cos(_t * 0.5 + _seed) * roam * 0.5 + sin(_t * 3.1) * 6.0 - 18.0)
	var next := _home + p
	flip_h = next.x < position.x
	position = next.round()
