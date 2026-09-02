class_name WaveDirector
extends Node2D
## Drives the scripted arena waves used by Act 3's skirmish and Act 5's battles.
##
## Chapter 1 battles cannot be lost. On death the player is pulled out of the
## line by an ally, takes a relationship hit, and the wave restarts: canon does
## not permit Torren to die at the Whispering Wood.

signal wave_started(index: int)
signal wave_cleared(index: int)
signal battle_finished()

const ENEMY_DIR := "res://scenes/actors/enemies/"

@export var act_id: String = ""
@export var scene_id: String = ""
@export var pull_out_penalty: int = -1
@export var pull_out_npc: String = "hune"

var waves: Array = []
var current_index: int = -1

var _alive: Array[Node] = []
var _spawn_points: Array[Marker2D] = []
var _player: CombatActor = null


func _ready() -> void:
	for child in get_children():
		if child is Marker2D:
			_spawn_points.append(child)
	waves = DialogueSystem.get_scene(act_id, scene_id).get("waves", [])
	_player = get_tree().get_first_node_in_group("player") as CombatActor
	if _player != null:
		_player.died.connect(_on_player_down)


func start() -> void:
	current_index = -1
	_next_wave()


func _next_wave() -> void:
	current_index += 1
	if current_index >= waves.size():
		battle_finished.emit()
		return
	_spawn_wave(waves[current_index])
	wave_started.emit(current_index)


func _spawn_wave(wave: Dictionary) -> void:
	_alive.clear()
	var slot := 0
	for group in wave.get("enemies", []):
		var path := ENEMY_DIR + String(group["type"]) + ".tscn"
		if not ResourceLoader.exists(path):
			push_error("WaveDirector: no enemy scene at %s" % path)
			continue
		var packed := load(path) as PackedScene
		for i in int(group.get("count", 1)):
			var enemy := packed.instantiate()
			if _spawn_points.size() > 0:
				enemy.global_position = _spawn_points[slot % _spawn_points.size()].global_position
			slot += 1
			get_parent().add_child(enemy)
			_alive.append(enemy)
			if enemy is CombatActor:
				(enemy as CombatActor).died.connect(_on_enemy_died.bind(enemy))


func _on_enemy_died(enemy: Node) -> void:
	_alive.erase(enemy)
	if not _alive.is_empty():
		return
	var wave: Dictionary = waves[current_index]
	wave_cleared.emit(current_index)
	# The between-wave narrative beat, if the act file names one.
	if wave.has("on_clear_node"):
		DialogueSystem.start_scene(act_id, scene_id, String(wave["on_clear_node"]))
		await DialogueSystem.dialogue_ended
	_next_wave()


## Fail-forward. The wave restarts; the story does not.
func _on_player_down() -> void:
	GameManager.adjust_relationship(pull_out_npc, pull_out_penalty)
	for enemy in _alive:
		if is_instance_valid(enemy):
			enemy.queue_free()
	_alive.clear()
	if _player != null:
		_player.hp = _player.max_hp
		_player.state = CombatActor.State.IDLE
		_player.health_changed.emit(_player.hp, _player.max_hp)
	current_index -= 1
	_next_wave()
