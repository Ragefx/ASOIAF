class_name CombatActor
extends CharacterBody2D
## Shared by the player and every enemy. Real-time, committal, no cancels.

signal died()
signal health_changed(hp: int, max_hp: int)
signal stamina_changed(stamina: float, max_stamina: float)

enum State { IDLE, MOVE, ATTACK, RECOVER, HURT, DODGE, DEAD }

@export var max_hp: int = 40
@export var attack_power: int = 6
@export var armor: int = 2
@export var poise: int = 2
@export var max_stamina: float = 100.0
@export var stamina_regen: float = 22.0
@export var walk_speed: float = 60.0
@export var run_speed: float = 95.0

var hp: int
var stamina: float
var state: State = State.IDLE
var facing: Vector2 = Vector2.DOWN

@onready var hitbox: Area2D = get_node_or_null("Hitbox")
@onready var hurtbox: Area2D = get_node_or_null("Hurtbox")


func _ready() -> void:
	hp = max_hp
	stamina = max_stamina
	if hitbox != null:
		set_hitbox_active(false)
		hitbox.area_entered.connect(_on_hitbox_hit)


func _physics_process(delta: float) -> void:
	if state != State.DODGE and state != State.ATTACK:
		stamina = minf(stamina + stamina_regen * delta, max_stamina)
		stamina_changed.emit(stamina, max_stamina)


## Active only on attack frames, so a swing that has finished cannot damage.
func set_hitbox_active(active: bool) -> void:
	if hitbox == null:
		return
	hitbox.monitoring = active
	for shape in hitbox.get_children():
		if shape is CollisionShape2D:
			shape.set_deferred("disabled", not active)


func spend_stamina(amount: float) -> bool:
	if stamina < amount:
		return false
	stamina -= amount
	stamina_changed.emit(stamina, max_stamina)
	return true


## Damage is flat minus armor with a small roll. No crits: the fantasy is a
## soldier in a line, not a rogue.
func take_damage(amount: int, from: Node = null) -> void:
	if state == State.DEAD or state == State.DODGE:
		return
	var rolled := int(round(amount * randf_range(0.9, 1.1)))
	var dealt := maxi(1, rolled - armor)
	hp = maxi(0, hp - dealt)
	health_changed.emit(hp, max_hp)

	if hp == 0:
		state = State.DEAD
		set_hitbox_active(false)
		died.emit()
		return

	# Poise decides whether a hit interrupts. Heavy actors keep swinging.
	if dealt > poise:
		state = State.HURT
		if from is Node2D:
			velocity = (global_position - (from as Node2D).global_position).normalized() * 90.0


func heal(amount: int) -> void:
	hp = mini(max_hp, hp + amount)
	health_changed.emit(hp, max_hp)


func _on_hitbox_hit(area: Area2D) -> void:
	var target := area.get_parent()
	if target is CombatActor and target != self:
		(target as CombatActor).take_damage(attack_power, self)
