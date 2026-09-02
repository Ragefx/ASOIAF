extends Node
## The state of record. Nothing else in the project owns persistent state.
##
## Flags, traits and relationships are read by everyone and written only through
## the methods here, so that every change emits a signal and the UI never polls.

signal flag_changed(flag: String, value: bool)
signal trait_changed(trait_name: String, value: int)
signal relationship_changed(npc_id: String, value: int)
signal act_changed(act_id: String)
signal pov_changed(pov: String)

const TRAIT_AXES := ["bold", "honest", "merciful", "loyal"]
const RELATIONSHIP_MIN := -10
const RELATIONSHIP_MAX := 10

var flags: Dictionary = {}
var traits: Dictionary = {}
var relationships: Dictionary = {}

var current_act: String = ""
var current_pov: String = ""

## Loaded once from data/npcs/protagonists.json. Drives the {knight}/{girl}/{house}
## text tokens, so renaming a protagonist is a one-file edit.
var protagonists: Dictionary = {}
var tokens: Dictionary = {}


func _ready() -> void:
	for axis in TRAIT_AXES:
		traits[axis] = 0
	_load_protagonists()


func _load_protagonists() -> void:
	var path := "res://data/npcs/protagonists.json"
	if not FileAccess.file_exists(path):
		push_error("GameManager: missing %s" % path)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("GameManager: %s is not a JSON object" % path)
		return
	protagonists = parsed.get("protagonists", {})
	tokens = parsed.get("tokens", {})


# --- flags -------------------------------------------------------------------

func set_flag(flag: String, value: bool = true) -> void:
	if flags.get(flag, false) == value:
		return
	flags[flag] = value
	flag_changed.emit(flag, value)


func has_flag(flag: String) -> bool:
	return flags.get(flag, false)


## Evaluates a requires_flags list. Entries are ANDed; a leading "!" negates.
func check_flags(required: Array) -> bool:
	for entry in required:
		var flag := String(entry)
		if flag.begins_with("!"):
			if has_flag(flag.substr(1)):
				return false
		elif not has_flag(flag):
			return false
	return true


# --- traits ------------------------------------------------------------------

func adjust_trait(trait_name: String, delta: int) -> void:
	if delta == 0:
		return
	traits[trait_name] = int(traits.get(trait_name, 0)) + delta
	trait_changed.emit(trait_name, traits[trait_name])


func get_trait(trait_name: String) -> int:
	return int(traits.get(trait_name, 0))


# --- relationships -----------------------------------------------------------

func adjust_relationship(npc_id: String, delta: int) -> void:
	if delta == 0:
		return
	var value := clampi(
		int(relationships.get(npc_id, 0)) + delta, RELATIONSHIP_MIN, RELATIONSHIP_MAX
	)
	if value == relationships.get(npc_id, 0):
		return
	relationships[npc_id] = value
	relationship_changed.emit(npc_id, value)


func get_relationship(npc_id: String) -> int:
	return int(relationships.get(npc_id, 0))


# --- act / pov ---------------------------------------------------------------

func set_act(act_id: String, pov: String) -> void:
	if current_act != act_id:
		current_act = act_id
		act_changed.emit(act_id)
	if current_pov != pov:
		current_pov = pov
		pov_changed.emit(pov)


# --- effects -----------------------------------------------------------------

## Applies the sets_flags / traits / relationship block carried by a dialogue
## node or choice. Called on node exit so effects land exactly once.
func apply_effects(source: Dictionary) -> void:
	for flag in source.get("sets_flags", []):
		set_flag(String(flag), true)
	for trait_name in source.get("traits", {}):
		adjust_trait(String(trait_name), int(source["traits"][trait_name]))
	for npc_id in source.get("relationship", {}):
		adjust_relationship(String(npc_id), int(source["relationship"][npc_id]))


## Substitutes {knight}, {girl}, {house} and friends at display time.
func substitute_tokens(text: String) -> String:
	var out := text
	for key in tokens:
		out = out.replace("{%s}" % key, String(tokens[key]))
	return out


# --- save/load ---------------------------------------------------------------

func to_dict() -> Dictionary:
	return {
		"flags": flags.duplicate(true),
		"traits": traits.duplicate(true),
		"relationships": relationships.duplicate(true),
		"act": current_act,
		"pov": current_pov,
	}


func from_dict(data: Dictionary) -> void:
	flags = data.get("flags", {}).duplicate(true)
	traits = data.get("traits", {}).duplicate(true)
	relationships = data.get("relationships", {}).duplicate(true)
	for axis in TRAIT_AXES:
		if not traits.has(axis):
			traits[axis] = 0
	current_act = data.get("act", "")
	current_pov = data.get("pov", "")
	act_changed.emit(current_act)
	pov_changed.emit(current_pov)
