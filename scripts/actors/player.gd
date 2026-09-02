extends CombatActor
## Free-roaming, four-directional, not grid-locked.
##
## Facing is derived from the dominant axis of input and is deliberately sticky:
## a diagonal keeps the last committed facing instead of flickering between two
## animations, which is the whole difference between this feeling like Zelda and
## feeling like a physics demo.

const LIGHT_CHAIN_WINDOW := 0.35
const ATTACK_ACTIVE := 0.12
const ATTACK_RECOVER := 0.22
const DODGE_TIME := 0.28
const DODGE_IFRAMES := 0.2
const DODGE_SPEED := 210.0
const DODGE_COST := 25.0
const HEAVY_COST := 30.0

@export var can_fight: bool = true   ## false for Nyra: Acts 2 and 4 have no combat

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var interact_area: Area2D = $InteractArea

var _chain_step: int = 0
var _chain_timer: float = 0.0
var _state_timer: float = 0.0
var _input_locked: bool = false


func _unhandled_input(event: InputEvent) -> void:
	if _input_locked or DialogueSystem.is_running:
		return
	if event.is_action_pressed("interact"):
		_try_interact()
	elif can_fight and event.is_action_pressed("attack_light"):
		_start_attack()
	elif can_fight and event.is_action_pressed("dodge"):
		_start_dodge()


func _physics_process(delta: float) -> void:
	super._physics_process(delta)
	_chain_timer = maxf(0.0, _chain_timer - delta)
	if _chain_timer == 0.0:
		_chain_step = 0

	match state:
		State.ATTACK, State.RECOVER, State.DODGE, State.HURT:
			_tick_timed_state(delta)
		State.DEAD:
			velocity = Vector2.ZERO
		_:
			_handle_movement()

	move_and_slide()
	_update_animation()


func _handle_movement() -> void:
	if _input_locked or DialogueSystem.is_running:
		velocity = Vector2.ZERO
		state = State.IDLE
		return

	var input := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if input == Vector2.ZERO:
		velocity = Vector2.ZERO
		state = State.IDLE
		return

	var speed := run_speed if Input.is_action_pressed("run") else walk_speed
	velocity = input.normalized() * speed
	facing = _resolve_facing(input)
	state = State.MOVE


## Dominant-axis facing with hysteresis: only change facing when one axis clearly
## wins, otherwise keep what we had.
func _resolve_facing(input: Vector2) -> Vector2:
	if absf(input.x) > absf(input.y) * 1.2:
		return Vector2.RIGHT if input.x > 0.0 else Vector2.LEFT
	if absf(input.y) > absf(input.x) * 1.2:
		return Vector2.DOWN if input.y > 0.0 else Vector2.UP
	return facing


func _tick_timed_state(delta: float) -> void:
	_state_timer -= delta
	if _state_timer > 0.0:
		return
	match state:
		State.ATTACK:
			set_hitbox_active(false)
			state = State.RECOVER
			_state_timer = ATTACK_RECOVER
		State.DODGE:
			state = State.IDLE
			velocity = Vector2.ZERO
		_:
			state = State.IDLE
			velocity = Vector2.ZERO


func _start_attack() -> void:
	if state in [State.ATTACK, State.DODGE, State.DEAD, State.HURT]:
		return
	# The chain only continues inside the window; outside it, we start over.
	_chain_step = (_chain_step + 1) if _chain_timer > 0.0 else 1
	_chain_step = mini(_chain_step, 3)
	_chain_timer = LIGHT_CHAIN_WINDOW

	state = State.ATTACK
	_state_timer = ATTACK_ACTIVE
	velocity = Vector2.ZERO
	if hitbox != null:
		hitbox.position = facing * 10.0
	set_hitbox_active(true)


func _start_dodge() -> void:
	if state in [State.DODGE, State.DEAD] or not spend_stamina(DODGE_COST):
		return
	state = State.DODGE
	_state_timer = DODGE_TIME
	velocity = facing * DODGE_SPEED
	# i-frames are shorter than the roll, so the recovery tail is punishable.
	if hurtbox != null:
		hurtbox.set_deferred("monitorable", false)
		get_tree().create_timer(DODGE_IFRAMES).timeout.connect(
			func() -> void: hurtbox.set_deferred("monitorable", true)
		)


func _try_interact() -> void:
	for area in interact_area.get_overlapping_areas():
		var target := area.get_parent()
		if target.has_method("interact"):
			target.interact()
			return


func _update_animation() -> void:
	if sprite == null:
		return
	var dir := _facing_name()
	var anim := "idle"
	match state:
		State.MOVE:
			anim = "walk"
		State.ATTACK:
			anim = "attack%d" % _chain_step
		State.DODGE:
			anim = "dodge"
		State.HURT:
			anim = "hurt"
		State.DEAD:
			anim = "dead"
	var wanted := "%s_%s" % [anim, dir]
	if sprite.sprite_frames != null and sprite.sprite_frames.has_animation(wanted):
		if sprite.animation != wanted:
			sprite.play(wanted)


func _facing_name() -> String:
	if facing == Vector2.UP:
		return "up"
	if facing == Vector2.LEFT:
		return "left"
	if facing == Vector2.RIGHT:
		return "right"
	return "down"


## Used by cutscenes and the Bran-carrying walk in Act 1, which deliberately
## disables running.
func set_input_locked(locked: bool) -> void:
	_input_locked = locked
	if locked:
		velocity = Vector2.ZERO
		state = State.IDLE
