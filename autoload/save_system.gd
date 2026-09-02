extends Node
## JSON saves, human-readable, at user://saves/slot_<n>.json.
## Slot 0 is reserved for autosaves (act change and level transition).

signal game_saved(slot: int)
signal game_loaded(slot: int)

const SAVE_DIR := "user://saves"
const VERSION := 1
const AUTOSAVE_SLOT := 0


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(SAVE_DIR)


func slot_path(slot: int) -> String:
	return "%s/slot_%d.json" % [SAVE_DIR, slot]


func has_save(slot: int) -> bool:
	return FileAccess.file_exists(slot_path(slot))


func save_game(slot: int) -> bool:
	var payload := {
		"version": VERSION,
		"saved_at": Time.get_datetime_string_from_system(),
		"level": SceneDirector.current_level,
		"spawn": SceneDirector.current_spawn,
		"quests": QuestSystem.to_dict(),
	}
	payload.merge(GameManager.to_dict())

	var file := FileAccess.open(slot_path(slot), FileAccess.WRITE)
	if file == null:
		push_error("SaveSystem: cannot write slot %d: %s" % [slot, FileAccess.get_open_error()])
		return false
	file.store_string(JSON.stringify(payload, "  "))
	file.close()
	game_saved.emit(slot)
	return true


func autosave() -> void:
	save_game(AUTOSAVE_SLOT)


func load_game(slot: int) -> bool:
	if not has_save(slot):
		return false
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(slot_path(slot)))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("SaveSystem: slot %d is not a JSON object" % slot)
		return false

	var data: Dictionary = _migrate(parsed)
	GameManager.from_dict(data)
	QuestSystem.from_dict(data.get("quests", {}))
	game_loaded.emit(slot)
	SceneDirector.goto_level(String(data.get("level", "")), String(data.get("spawn", "")))
	return true


## Older saves are migrated rather than rejected. Each step upgrades by one
## version, so a very old save walks the whole chain.
func _migrate(data: Dictionary) -> Dictionary:
	var version := int(data.get("version", 0))
	while version < VERSION:
		match version:
			0:
				# Pre-versioned saves had no quest block.
				if not data.has("quests"):
					data["quests"] = { "active": [], "complete": [] }
			_:
				push_warning("SaveSystem: no migration from version %d" % version)
				break
		version += 1
		data["version"] = version
	return data


func describe(slot: int) -> Dictionary:
	if not has_save(slot):
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(slot_path(slot)))
	if typeof(parsed) != TYPE_DICTIONARY:
		return {}
	return {
		"act": parsed.get("act", ""),
		"pov": parsed.get("pov", ""),
		"level": parsed.get("level", ""),
		"saved_at": parsed.get("saved_at", ""),
	}
