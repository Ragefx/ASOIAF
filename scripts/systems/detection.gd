class_name Detection
extends Node
## Nyra's threat resource for Acts 2 and 4. She has no HP bar; being seen is how
## she takes damage.
##
## Nothing here can fail a scene. At maximum the scene fails forward - she is
## caught, a flag is set, and the story continues worse. The player is never sent
## back to a checkpoint for being seen.

signal detection_changed(value: int, maximum: int)
signal caught()

const MAX := 4
const DECAY_DELAY := 3.0
const DECAY_RATE := 1.0    ## points per second once decay starts

## Carrying something justifies her presence; empty hands make her a girl
## loitering. This is the act's core verb, not a modifier.
@export var carrying: bool = false
@export var caught_flag: String = ""

var value: float = 0.0
var _time_since_seen: float = 0.0


func _process(delta: float) -> void:
	_time_since_seen += delta
	if _time_since_seen < DECAY_DELAY or value <= 0.0:
		return
	var before := int(value)
	value = maxf(0.0, value - DECAY_RATE * delta)
	if int(value) != before:
		detection_changed.emit(int(value), MAX)


func seen(amount: float = 1.0) -> void:
	_time_since_seen = 0.0
	# Carrying halves the cost of being looked at, and never below one tick.
	var cost := amount * 0.5 if carrying else amount
	var before := int(value)
	value = minf(MAX, value + cost)
	if int(value) != before:
		detection_changed.emit(int(value), MAX)
	if value >= MAX:
		_on_caught()


func reset() -> void:
	value = 0.0
	detection_changed.emit(0, MAX)


func _on_caught() -> void:
	if caught_flag != "":
		GameManager.set_flag(caught_flag, true)
	caught.emit()
	reset()
