extends Node
## Objectives complete when a flag is set, so quests subscribe to
## GameManager.flag_changed and need no event plumbing of their own.

signal quest_started(quest_id: String)
signal objective_completed(quest_id: String, objective_id: String)
signal quest_completed(quest_id: String)

const QUEST_PATH := "res://data/quests/chapter1_quests.json"

var quests: Dictionary = {}          ## quest_id -> definition
var active: Array[String] = []
var complete: Array[String] = []


func _ready() -> void:
	_load_quests()
	GameManager.flag_changed.connect(_on_flag_changed)


func _load_quests() -> void:
	if not FileAccess.file_exists(QUEST_PATH):
		push_error("QuestSystem: missing %s" % QUEST_PATH)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(QUEST_PATH))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("QuestSystem: %s is not a JSON object" % QUEST_PATH)
		return
	for quest in parsed.get("quests", []):
		quests[String(quest["id"])] = quest


func start_quest(quest_id: String) -> void:
	if quest_id in active or quest_id in complete or not quests.has(quest_id):
		return
	active.append(quest_id)
	quest_started.emit(quest_id)


## Every quest belonging to an act is started when that act begins.
func start_act_quests(act_id: String) -> void:
	for quest_id in quests:
		if quests[quest_id].get("act") == act_id:
			start_quest(quest_id)


func is_objective_complete(quest_id: String, objective_id: String) -> bool:
	for obj in quests.get(quest_id, {}).get("objectives", []):
		if obj["id"] == objective_id:
			return GameManager.has_flag(String(obj["flag"]))
	return false


## Objectives of an ordered quest are hidden until the one before them is done,
## so the journal reads as a sequence rather than a spoiler list.
func visible_objectives(quest_id: String) -> Array:
	var quest: Dictionary = quests.get(quest_id, {})
	var objectives: Array = quest.get("objectives", [])
	if not quest.get("ordered", false):
		return objectives
	var out: Array = []
	for obj in objectives:
		out.append(obj)
		if not GameManager.has_flag(String(obj["flag"])):
			break
	return out


func _on_flag_changed(flag: String, value: bool) -> void:
	if not value:
		return
	for quest_id in active.duplicate():
		var quest: Dictionary = quests[quest_id]
		for obj in quest.get("objectives", []):
			if obj["flag"] == flag:
				objective_completed.emit(quest_id, String(obj["id"]))
		if quest.get("completion_flag") == flag:
			active.erase(quest_id)
			complete.append(quest_id)
			quest_completed.emit(quest_id)


func to_dict() -> Dictionary:
	return { "active": active.duplicate(), "complete": complete.duplicate() }


func from_dict(data: Dictionary) -> void:
	active.assign(data.get("active", []))
	complete.assign(data.get("complete", []))
