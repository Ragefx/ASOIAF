extends Sprite2D
## Dawn mist over the level: a tiling texture drifting slowly, which burns off
## (fades out) once `clears_on_flag` is set - in the opening scene, when the drill
## is done and the sun is properly up. Purely visual; above actors, below the UI.

@export var drift := Vector2(6.0, 1.5)   ## texture px per second
@export var clears_on_flag: String = ""
@export var clear_time: float = 6.0

var _offset := Vector2.ZERO


func _ready() -> void:
	if clears_on_flag != "":
		if GameManager.has_flag(clears_on_flag):
			modulate.a = 0.0
		GameManager.flag_changed.connect(_on_flag_changed)


func _process(delta: float) -> void:
	_offset += drift * delta
	region_rect.position = _offset.round()


func _on_flag_changed(flag: String, value: bool) -> void:
	if flag == clears_on_flag and value:
		create_tween().tween_property(self, "modulate:a", 0.0, clear_time)
