extends CanvasLayer
## Esc pauses the game: Resume, New game, Quit. The game otherwise always continues
## from its autosave on launch (scripts/ui/main.gd), so this is the only way back to
## the start of Chapter 1 short of deleting user://saves by hand. New game asks twice.

var _panel: Control
var _new_game: Button
var _confirming := false


func _ready() -> void:
	layer = 90
	process_mode = Node.PROCESS_MODE_ALWAYS
	_build()
	_panel.visible = false


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel") and not SceneDirector.is_transitioning:
		_set_open(not _panel.visible)
		get_viewport().set_input_as_handled()


func _set_open(open: bool) -> void:
	_panel.visible = open
	get_tree().paused = open
	_confirming = false
	_new_game.text = "New game"
	if open:
		_panel.get_node("Box/Resume").grab_focus()


func _build() -> void:
	_panel = ColorRect.new()
	(_panel as ColorRect).color = Color(0.03, 0.04, 0.06, 0.72)
	_panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_panel)
	var box := VBoxContainer.new()
	box.name = "Box"
	box.set_anchors_preset(Control.PRESET_CENTER)
	box.add_theme_constant_override("separation", 10)
	box.custom_minimum_size = Vector2(220, 0)
	box.position = Vector2(-110, -80)
	_panel.add_child(box)
	var title := Label.new()
	title.text = "Paused"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(title)
	_add_button(box, "Resume", "Resume", func() -> void: _set_open(false))
	_new_game = _add_button(box, "NewGame", "New game", _on_new_game)
	_add_button(box, "Quit", "Quit", func() -> void: get_tree().quit())


func _add_button(box: Control, node_name: String, text: String, action: Callable) -> Button:
	var b := Button.new()
	b.name = node_name
	b.text = text
	b.pressed.connect(action)
	box.add_child(b)
	return b


func _on_new_game() -> void:
	if not _confirming:
		_confirming = true
		_new_game.text = "Start over? Press again"
		return
	_set_open(false)
	start_new_game()


## Forgets the autosave and every flag, trait and quest, then opens Chapter 1 as a
## first launch would.
func start_new_game() -> void:
	if SaveSystem.has_save(SaveSystem.AUTOSAVE_SLOT):
		DirAccess.remove_absolute(SaveSystem.slot_path(SaveSystem.AUTOSAVE_SLOT))
	if DialogueSystem.is_running:
		DialogueSystem._finish()
	GameManager.from_dict({})
	QuestSystem.from_dict({})
	SceneDirector.current_level = ""
	SceneDirector.begin_act("act_1")
