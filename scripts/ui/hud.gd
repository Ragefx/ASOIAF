extends CanvasLayer
## Torren gets a health and stamina bar. Nyra gets a detection meter and no
## health bar at all, because she cannot be hurt in the way he can.

@onready var health_bar: ProgressBar = $Combat/HealthBar
@onready var stamina_bar: ProgressBar = $Combat/StaminaBar
@onready var combat_group: Control = $Combat
@onready var detection_group: Control = $Detection
@onready var detection_bar: ProgressBar = $Detection/DetectionBar
@onready var objective_label: Label = $ObjectiveLabel
@onready var hint_label: Label = $HintLabel

## Control hints for the opening scene, which is the movement / attack / talk
## tutorial. First entry for the current level whose flags hold wins; hidden while
## dialogue is up. (Scene-level "sets_flags" in the act files are documentation and
## never set at runtime, so hints key off the level plus real flags.)
const HINTS := [
	{"level": "winterfell_training_yard", "flags": ["act1_heard_king_coming"], "text": "Follow the track south"},
	{"level": "winterfell_training_yard", "flags": ["act1_drill_done"], "text": "E  to talk   ·   Ser Cley is by the fence"},
	{"level": "winterfell_training_yard", "flags": [], "text": "WASD  to move   ·   Left mouse  to swing"},
]

var _player: CombatActor = null
var _detection: Detection = null


func _ready() -> void:
	GameManager.pov_changed.connect(_on_pov_changed)
	QuestSystem.objective_completed.connect(_refresh_objective)
	QuestSystem.quest_started.connect(_refresh_objective.bind(""))
	SceneDirector.level_changed.connect(_on_level_changed)
	GameManager.flag_changed.connect(func(_f: String, _v: bool) -> void: _refresh_hint())
	DialogueSystem.dialogue_started.connect(func(_a: String, _s: String) -> void: _refresh_hint())
	DialogueSystem.dialogue_ended.connect(func(_a: String, _s: String) -> void: _refresh_hint())
	_on_pov_changed(GameManager.current_pov)


func _on_level_changed(_level_id: String) -> void:
	_bind_player()
	_refresh_objective("", "")
	_refresh_hint()


func _refresh_hint() -> void:
	hint_label.text = ""
	if DialogueSystem.is_running:
		return
	for hint in HINTS:
		if hint["level"] == SceneDirector.current_level and GameManager.check_flags(hint["flags"]):
			hint_label.text = String(hint["text"])
			return


func _bind_player() -> void:
	_player = get_tree().get_first_node_in_group("player") as CombatActor
	if _player == null:
		return
	if not _player.health_changed.is_connected(_on_health_changed):
		_player.health_changed.connect(_on_health_changed)
		_player.stamina_changed.connect(_on_stamina_changed)
	_on_health_changed(_player.hp, _player.max_hp)

	_detection = _player.get_node_or_null("Detection") as Detection
	if _detection != null and not _detection.detection_changed.is_connected(_on_detection_changed):
		_detection.detection_changed.connect(_on_detection_changed)


func _on_pov_changed(pov: String) -> void:
	var is_knight := pov == "torren"
	combat_group.visible = is_knight
	detection_group.visible = not is_knight


func _on_health_changed(hp: int, max_hp: int) -> void:
	health_bar.max_value = max_hp
	health_bar.value = hp


func _on_stamina_changed(stamina: float, max_stamina: float) -> void:
	stamina_bar.max_value = max_stamina
	stamina_bar.value = stamina


func _on_detection_changed(value: int, maximum: int) -> void:
	detection_bar.max_value = maximum
	detection_bar.value = value


func _refresh_objective(_a: String, _b: String) -> void:
	for quest_id in QuestSystem.active:
		var visible: Array = QuestSystem.visible_objectives(quest_id)
		for obj in visible:
			if not GameManager.has_flag(String(obj["flag"])):
				objective_label.text = String(obj["text"])
				return
	objective_label.text = ""
