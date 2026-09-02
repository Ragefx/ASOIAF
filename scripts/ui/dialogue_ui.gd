extends CanvasLayer
## Renders whatever DialogueSystem emits. Knows nothing about flags: choices that
## fail their conditions are filtered out before they reach here.

const PORTRAIT_DIR := "res://assets/portraits/"
const CHARS_PER_SECOND := 45.0

@onready var panel: Control = $Panel
@onready var name_label: Label = $Panel/NameLabel
@onready var text_label: RichTextLabel = $Panel/TextLabel
@onready var portrait: TextureRect = $Panel/Portrait
@onready var choices_box: VBoxContainer = $Panel/Choices
@onready var continue_hint: Control = $Panel/ContinueHint

var _full_text: String = ""
var _revealed: float = 0.0
var _awaiting_choice: bool = false


func _ready() -> void:
	panel.hide()
	DialogueSystem.line_shown.connect(_on_line_shown)
	DialogueSystem.choices_offered.connect(_on_choices_offered)
	DialogueSystem.dialogue_ended.connect(_on_dialogue_ended)


func _process(delta: float) -> void:
	if not panel.visible or _revealed >= _full_text.length():
		return
	_revealed = minf(_revealed + CHARS_PER_SECOND * delta, float(_full_text.length()))
	text_label.visible_characters = int(_revealed)
	continue_hint.visible = _revealed >= _full_text.length() and not _awaiting_choice


func _unhandled_input(event: InputEvent) -> void:
	if not panel.visible or _awaiting_choice:
		return
	if event.is_action_pressed("interact"):
		get_viewport().set_input_as_handled()
		# First press completes the reveal; second advances.
		if _revealed < _full_text.length():
			_revealed = float(_full_text.length())
			text_label.visible_characters = -1
		else:
			DialogueSystem.advance()


func _on_line_shown(speaker: String, portrait_key: String, text: String) -> void:
	panel.show()
	_clear_choices()
	_awaiting_choice = false

	var is_narrator := speaker == "narrator"
	name_label.visible = not is_narrator
	name_label.text = _speaker_name(speaker)
	portrait.visible = not is_narrator and portrait_key != ""
	if portrait.visible:
		var path := PORTRAIT_DIR + portrait_key + ".png"
		portrait.texture = load(path) if ResourceLoader.exists(path) else null

	# Narrator lines are the game's stage voice and are set in italics.
	_full_text = ("[i]%s[/i]" % text) if is_narrator else text
	text_label.text = _full_text
	text_label.visible_characters = 0
	_revealed = 0.0
	continue_hint.hide()


func _speaker_name(speaker: String) -> String:
	if GameManager.protagonists.has(speaker):
		return String(GameManager.protagonists[speaker]["display_name"])
	return String(NPC.get_record(speaker).get("name", speaker.capitalize()))


func _on_choices_offered(choices: Array) -> void:
	_awaiting_choice = true
	continue_hint.hide()
	_clear_choices()
	for i in choices.size():
		var button := Button.new()
		button.text = GameManager.substitute_tokens(String(choices[i]["text"]))
		button.pressed.connect(_on_choice_pressed.bind(i))
		choices_box.add_child(button)
	if choices_box.get_child_count() > 0:
		(choices_box.get_child(0) as Button).grab_focus()


func _on_choice_pressed(index: int) -> void:
	_awaiting_choice = false
	_clear_choices()
	DialogueSystem.choose(index)


func _clear_choices() -> void:
	for child in choices_box.get_children():
		child.queue_free()


func _on_dialogue_ended(_act_id: String, _scene_id: String) -> void:
	panel.hide()
	_clear_choices()
	_awaiting_choice = false
