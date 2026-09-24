extends Area2D
## Walk into it to leave the level - once the scene's story allows it.
##
## Until `requires_flags` are met it does nothing (the player just walks on). Once
## they are, it moves the player to `target_level`/`target_spawn`. If that level
## doesn't exist yet - the build runs ahead of the art - it shows `unbuilt_card`
## instead of erroring, so a scene can be finished and played before the next one.

@export var target_level: String = ""
@export var target_spawn: String = ""
@export var requires_flags: Array[String] = []
@export_multiline var unbuilt_card: String = "To be continued."

var _used := false


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node) -> void:
	if _used or not body.is_in_group("player") or not GameManager.check_flags(requires_flags):
		return
	_used = true
	if ResourceLoader.exists("res://scenes/world/%s.tscn" % target_level):
		SceneDirector.goto_level(target_level, target_spawn)
	else:
		_show_card()


func _show_card() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 50
	var shade := ColorRect.new()
	shade.color = Color(0, 0, 0, 0)
	shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var label := Label.new()
	label.text = unbuilt_card
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.set_anchors_preset(Control.PRESET_FULL_RECT)
	label.modulate.a = 0.0
	layer.add_child(shade)
	layer.add_child(label)
	get_tree().root.add_child(layer)
	var t := layer.create_tween()
	t.tween_property(shade, "color:a", 0.85, 1.2)
	t.parallel().tween_property(label, "modulate:a", 1.0, 1.6)
