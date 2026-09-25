extends Node
## Shows or hides another node when a flag changes - the deserter is gone after the
## sentence, a banner goes up once the king is sighted. Checked on load too, so a
## saved game comes back the way it was left.

@export var target: NodePath
@export var flag: String = ""
@export var visible_when_set: bool = false


func _ready() -> void:
	GameManager.flag_changed.connect(func(f: String, _v: bool) -> void:
		if f == flag:
			_apply())
	_apply()


func _apply() -> void:
	var node := get_node_or_null(target) as CanvasItem
	if node != null:
		node.visible = GameManager.has_flag(flag) == visible_when_set
