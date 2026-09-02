extends Node
## Music beds with crossfade, plus a small SFX pool.
##
## Scene files name their music by key ("kl_service_quiet", "none"). "none" is
## meaningful in this game - several of Chapter 1's most important scenes are
## scored with silence, so it stops the bed rather than leaving the last one
## playing.

const MUSIC_DIR := "res://assets/audio/music/"
const SFX_DIR := "res://assets/audio/sfx/"
const CROSSFADE := 1.5
const SFX_VOICES := 8

var _a: AudioStreamPlayer
var _b: AudioStreamPlayer
var _active: AudioStreamPlayer
var _sfx: Array[AudioStreamPlayer] = []

var current_track: String = ""


func _ready() -> void:
	_a = _make_music_player()
	_b = _make_music_player()
	_active = _a
	for i in SFX_VOICES:
		var player := AudioStreamPlayer.new()
		player.bus = "SFX"
		add_child(player)
		_sfx.append(player)


func _make_music_player() -> AudioStreamPlayer:
	var player := AudioStreamPlayer.new()
	player.bus = "Music"
	add_child(player)
	return player


func play_music(track: String) -> void:
	if track == current_track:
		return
	current_track = track

	if track == "" or track == "none":
		stop_music()
		return

	var path := MUSIC_DIR + track + ".ogg"
	if not ResourceLoader.exists(path):
		push_warning("AudioManager: no music at %s" % path)
		return

	var incoming := _b if _active == _a else _a
	incoming.stream = load(path)
	incoming.volume_db = -40.0
	incoming.play()

	var tween := create_tween().set_parallel(true)
	tween.tween_property(incoming, "volume_db", 0.0, CROSSFADE)
	tween.tween_property(_active, "volume_db", -40.0, CROSSFADE)
	tween.chain().tween_callback(_active.stop)
	_active = incoming


func stop_music() -> void:
	var outgoing := _active
	var tween := create_tween()
	tween.tween_property(outgoing, "volume_db", -40.0, CROSSFADE)
	tween.tween_callback(outgoing.stop)


func play_sfx(name: String) -> void:
	var path := SFX_DIR + name + ".wav"
	if not ResourceLoader.exists(path):
		return
	for player in _sfx:
		if not player.playing:
			player.stream = load(path)
			player.play()
			return
