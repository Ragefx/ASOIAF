extends Node
## The only persistent scene. Levels are instanced into World and freed on
## transition, which is why every piece of state that must survive a transition
## lives in an autoload.

@onready var world: Node2D = $World
@onready var transition: CanvasLayer = $TransitionLayer


func _ready() -> void:
	SceneDirector.world_root = world
	SceneDirector.transition_layer = transition
	transition.modulate.a = 0.0

	# Continue from the autosave if there is one, otherwise open Chapter 1.
	if SaveSystem.has_save(SaveSystem.AUTOSAVE_SLOT):
		SaveSystem.load_game(SaveSystem.AUTOSAVE_SLOT)
	else:
		SceneDirector.begin_act("act_1")
