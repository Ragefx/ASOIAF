class_name NPC
extends CharacterBody2D
## NPCs resolve their name, portrait set and voice notes from data/npcs/npcs.json
## by npc_id, so a writer can add a character without touching a scene file.

@export var npc_id: String = ""
@export var dialogue_scene: String = ""      ## scene_id in the current act file
@export var dialogue_node: String = ""       ## entry node; blank uses the scene start
@export var wander: bool = false
@export var wander_radius: float = 24.0

## Prioritized routing rules, most specific first. The first rule whose flags are
## satisfied wins. This is how the same Jory can say something different before
## and after Bran's fall without a wall of ifs.
@export var dialogue_rules: Array[Dictionary] = []

var display_name: String = ""
var portrait_set: String = ""

@onready var sprite: AnimatedSprite2D = get_node_or_null("AnimatedSprite2D")

static var _npc_data: Dictionary = {}


func _ready() -> void:
	_load_data()
	var record: Dictionary = _npc_data.get(npc_id, {})
	display_name = String(record.get("name", npc_id))
	portrait_set = String(record.get("portrait_set", npc_id))
	if record.is_empty() and npc_id != "":
		push_warning("NPC: no data/npcs entry for %s" % npc_id)


static func _load_data() -> void:
	if not _npc_data.is_empty():
		return
	var path := "res://data/npcs/npcs.json"
	if not FileAccess.file_exists(path):
		push_error("NPC: missing %s" % path)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) == TYPE_DICTIONARY:
		_npc_data = parsed.get("npcs", {})


## Public lookup used by the dialogue UI to resolve a speaker id to a name.
static func get_record(id: String) -> Dictionary:
	_load_data()
	return _npc_data.get(id, {})


func interact() -> void:
	if DialogueSystem.is_running:
		return
	var route := _resolve_route()
	if route.is_empty():
		return
	DialogueSystem.start_scene(
		GameManager.current_act, String(route["scene"]), String(route.get("node", ""))
	)


func _resolve_route() -> Dictionary:
	for rule in dialogue_rules:
		if GameManager.check_flags(rule.get("requires_flags", [])):
			return {
				"scene": rule.get("scene_id", dialogue_scene),
				"node": rule.get("node", ""),
			}
	if dialogue_scene == "":
		return {}
	return { "scene": dialogue_scene, "node": dialogue_node }


## NPCs read their own relationship value to pick greeting lines; the scene file
## does the rest with requires_flags.
func relationship() -> int:
	return GameManager.get_relationship(npc_id)
