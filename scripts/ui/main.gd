extends Node
## The only persistent scene. Levels are instanced into World and freed on
## transition, which is why every piece of state that must survive a transition
## lives in an autoload.

@onready var world: Node2D = $World
## The fade target is the ColorRect, not its parent CanvasLayer - CanvasLayer
## extends Node, not CanvasItem, so it has no "modulate" for SceneDirector's
## tweens to animate. Handing CanvasLayer itself around here would break every
## fade the first time one ran.
@onready var transition: ColorRect = $TransitionLayer/Fade

## The smallest view anyone gets, in game pixels (project.godot's viewport size).
## Every game pixel is drawn as a whole number of screen pixels - 2x on 1080p and
## 1440p - and a larger screen shows more world around the player rather than
## bigger pixels. See docs/STYLE_GUIDE.md section 0.
const BASE_VIEW := Vector2i(960, 540)


func _ready() -> void:
	SceneDirector.world_root = world
	SceneDirector.transition_layer = transition
	transition.modulate.a = 0.0
	get_tree().root.size_changed.connect(_fit_view)
	_fit_view()

	# `-- --world=winterfell` opens a world site to walk freely, outside the story
	# (docs/WORLD_DESIGN.md milestone 1); nothing is saved from it.
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--world="):
			SaveSystem.autosave_enabled = false
			GameManager.current_pov = "torren"
			SceneDirector.goto_level(arg.trim_prefix("--world="), "main_gate")
			return
	# Continue from the autosave if there is one, otherwise open Chapter 1.
	if SaveSystem.has_save(SaveSystem.AUTOSAVE_SLOT):
		SaveSystem.load_game(SaveSystem.AUTOSAVE_SLOT)
	else:
		SceneDirector.begin_act("act_1")


## Godot's own "expand + integer scaling" pins the view at BASE_VIEW and letterboxes
## the remainder (a 2560x1440 screen got a 1920x1080 picture with black borders), so
## the view is sized here instead: the largest whole-number scale at which BASE_VIEW
## still fits, then as much world as fills the window at that scale.
func _fit_view() -> void:
	var root := get_tree().root
	var window := DisplayServer.window_get_size()
	var scale := maxi(1, mini(window.x / BASE_VIEW.x, window.y / BASE_VIEW.y))
	root.content_scale_size = Vector2i(window.x / scale, window.y / scale)
