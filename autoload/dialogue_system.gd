extends Node
## Loads act files and walks their dialogue graphs.
##
## Act files are cached after first parse and never re-read. Effects
## (sets_flags / traits / relationship) are applied on node exit, so a choice's
## effects land exactly once even if the UI is dismissed and reopened.

signal dialogue_started(act_id: String, scene_id: String)
signal line_shown(speaker: String, portrait: String, text: String)
signal choices_offered(choices: Array)
signal dialogue_ended(act_id: String, scene_id: String)

const SCENE_DIR := "res://data/scenes/"

var _acts: Dictionary = {}          ## act_id -> parsed act file
var _active_act: String = ""
var _active_scene: String = ""
var _nodes: Dictionary = {}
var _current_id: String = ""
var _pending_choices: Array = []

var is_running: bool = false


func get_act(act_id: String) -> Dictionary:
	if _acts.has(act_id):
		return _acts[act_id]
	var path := SCENE_DIR + act_id + ".json"
	if not FileAccess.file_exists(path):
		push_error("DialogueSystem: no act file at %s" % path)
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("DialogueSystem: %s is not a JSON object" % path)
		return {}
	_acts[act_id] = parsed
	return parsed


func get_scene(act_id: String, scene_id: String) -> Dictionary:
	for scene in get_act(act_id).get("scenes", []):
		if scene.get("scene_id") == scene_id:
			return scene
	return {}


## Entry point. Walks from the scene's declared start node, or from `from_node`
## when a trigger volume or wave director enters the graph part-way.
func start_scene(act_id: String, scene_id: String, from_node: String = "") -> void:
	var scene := get_scene(act_id, scene_id)
	if scene.is_empty():
		push_error("DialogueSystem: no scene %s in %s" % [scene_id, act_id])
		return
	_active_act = act_id
	_active_scene = scene_id
	_nodes = scene["dialogue"]["nodes"]
	is_running = true
	dialogue_started.emit(act_id, scene_id)
	_goto(from_node if from_node != "" else String(scene["dialogue"]["start"]))


## Advance past the current line. No-op while choices are pending - the UI must
## call choose() instead.
func advance() -> void:
	if not is_running or not _pending_choices.is_empty():
		return
	var node: Dictionary = _nodes.get(_current_id, {})
	GameManager.apply_effects(node)
	if node.get("end", false):
		_finish()
	elif node.has("next"):
		_goto(String(node["next"]))
	else:
		_finish()


func choose(index: int) -> void:
	if index < 0 or index >= _pending_choices.size():
		return
	var choice: Dictionary = _pending_choices[index]
	_pending_choices = []
	GameManager.apply_effects(_nodes.get(_current_id, {}))
	GameManager.apply_effects(choice)
	_goto(String(choice["next"]))


func _goto(node_id: String) -> void:
	if not _nodes.has(node_id):
		push_error("DialogueSystem: node %s not found in %s" % [node_id, _active_scene])
		_finish()
		return
	_current_id = node_id
	var node: Dictionary = _nodes[node_id]

	# A node whose conditions fail is skipped rather than shown.
	if not GameManager.check_flags(node.get("requires_flags", [])):
		if node.has("next"):
			_goto(String(node["next"]))
		else:
			_finish()
		return

	line_shown.emit(
		String(node.get("speaker", "narrator")),
		String(node.get("portrait", "")),
		GameManager.substitute_tokens(String(node.get("text", "")))
	)

	if node.has("choices"):
		_pending_choices = _filter_choices(node["choices"])
		if _pending_choices.is_empty():
			# Every branch was gated out. Fall through if the author gave a fallback.
			if node.has("fallback"):
				_goto(String(node["fallback"]))
			else:
				_finish()
			return
		choices_offered.emit(_pending_choices)


## Choices whose conditions fail never reach the UI, so the UI knows nothing
## about flags.
func _filter_choices(choices: Array) -> Array:
	var out: Array = []
	for choice in choices:
		if GameManager.check_flags(choice.get("requires_flags", [])):
			out.append(choice)
	return out


func _finish() -> void:
	is_running = false
	_pending_choices = []
	dialogue_ended.emit(_active_act, _active_scene)
