extends Node
## Where the story lets the player go: the state of every region and place in Westeros,
## worked out from the story flags (docs/WORLD_DESIGN.md §3, data/world/regions.json).
##
## A phase is reached when any of its flags is set. A region or place takes the state of
## the latest phase it lists that has been reached, or "open" before any. A place's own
## rules win over its region's. Nothing here is saved: it is always derived from the flags,
## so an old save gets the right world the moment it loads.

signal state_changed(id: String, state: String)

const DATA_PATH := "res://data/world/regions.json"
const OPEN := "open"

var _phases: Array = []            ## [{id, month, flags}], in story order
var _rules: Dictionary = {}        ## id -> [{from, state, why}]
var _region_of: Dictionary = {}    ## place id -> region id
var _names: Dictionary = {}        ## region id -> display name
var _current: Dictionary = {}      ## id -> state, to emit only on change


func _ready() -> void:
	_load()
	GameManager.flag_changed.connect(func(_f: String, _v: bool) -> void: _refresh())
	_refresh()


func _load() -> void:
	var file := FileAccess.open(DATA_PATH, FileAccess.READ)
	if file == null:
		push_error("WorldState: cannot open %s" % DATA_PATH)
		return
	var data: Dictionary = JSON.parse_string(file.get_as_text())
	_phases = data.get("phases", [])
	for region in data.get("regions", []):
		_rules[region["id"]] = region.get("states", [])
		_names[region["id"]] = region.get("name", region["id"])
		for site in region.get("sites", []):
			_region_of[site] = region["id"]
	for place in data.get("places", []):
		_rules[place["id"]] = place.get("states", [])


## Index of the latest phase reached, or -1 before the story starts.
func current_phase() -> int:
	var reached := -1
	for i in _phases.size():
		for flag in _phases[i]["flags"]:
			if GameManager.has_flag(String(flag)):
				reached = i
				break
	return reached


func phase_id() -> String:
	var i := current_phase()
	return String(_phases[i]["id"]) if i >= 0 else ""


## "open", "guarded", "closed", "contested" or "sealed" for a region or a place.
func state_of(id: String) -> String:
	return String(_rule_for(id).get("state", OPEN))


## The line a guard, a sign or a rumour gives for the state; "" when open.
func reason_for(id: String) -> String:
	return String(_rule_for(id).get("why", ""))


func region_of(place: String) -> String:
	return String(_region_of.get(place, ""))


func region_name(region: String) -> String:
	return String(_names.get(region, region))


## Can the player walk in? Contested places can be entered, at a risk.
func can_enter(id: String) -> bool:
	return state_of(id) in [OPEN, "guarded", "contested"]


func _rule_for(id: String) -> Dictionary:
	var own := _latest(_rules.get(id, []))
	if not own.is_empty():
		return own
	var region := region_of(id)
	return _latest(_rules.get(region, [])) if region != "" else {}


func _latest(rules: Array) -> Dictionary:
	var now := current_phase()
	var best: Dictionary = {}
	var best_at := -1
	for rule in rules:
		var at := _phase_index(String(rule["from"]))
		if at >= 0 and at <= now and at >= best_at:
			best = rule
			best_at = at
	return best


func _phase_index(id: String) -> int:
	for i in _phases.size():
		if _phases[i]["id"] == id:
			return i
	return -1


func _refresh() -> void:
	for id in _rules:
		var s := state_of(id)
		if _current.get(id, OPEN) != s:
			_current[id] = s
			state_changed.emit(id, s)
