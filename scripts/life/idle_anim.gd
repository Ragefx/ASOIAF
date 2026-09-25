extends AnimatedSprite2D
## Loops its animation from a random frame at a slightly random speed, so a row of
## banners or a pair of braziers never move in lockstep.

@export var anim: StringName = &"idle"


func _ready() -> void:
	play(anim)
	frame = randi() % maxi(1, sprite_frames.get_frame_count(anim))
	speed_scale = randf_range(0.85, 1.15)
