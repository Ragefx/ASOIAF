extends CombatActor
## A straw man on a post. Takes hits like any combat actor, so the player's normal
## hitbox code needs no special case, but never dies: it rocks on its post and
## counts. After `hits_needed` hits it sets `completion_flag` once - the opening
## scene's "Finish your drill" objective.

@export var hits_needed: int = 5
@export var completion_flag: String = ""

@onready var _sprite: Sprite2D = $Sprite2D

var hits: int = 0
var _wobble: Tween = null


func take_damage(_amount: int, from: Node = null) -> void:
	hits += 1
	_rock(from)
	if hits >= hits_needed and completion_flag != "" and not GameManager.has_flag(completion_flag):
		GameManager.set_flag(completion_flag)


## Tip away from the blow and settle back, pivoting on the post's base.
func _rock(from: Node) -> void:
	var side := 1.0
	if from is Node2D:
		side = signf(global_position.x - (from as Node2D).global_position.x)
		if side == 0.0:
			side = 1.0 if hits % 2 == 0 else -1.0
	if _wobble != null:
		_wobble.kill()
	_sprite.rotation = 0.0
	_wobble = create_tween()
	_wobble.tween_property(_sprite, "rotation", 0.28 * side, 0.06)
	_wobble.tween_property(_sprite, "rotation", -0.12 * side, 0.12)
	_wobble.tween_property(_sprite, "rotation", 0.0, 0.18)
