extends SceneTree
## Checks WorldState's story-driven region rules (docs/WORLD_DESIGN.md §3) headless:
##
##   godot --headless --path . -s tools/godot/test_world_state.gd

var failures := 0
var GM: Node
var WS: Node


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	GM = root.get_node("GameManager")
	WS = root.get_node("WorldState")
	GM.flags.clear()
	WS._refresh()

	_check(WS.phase_id() == "", "no phase before the story starts")
	_check(WS.state_of("the_north") == "open", "the North is open at the start")
	_check(WS.state_of("winterfell") == "open", "a site takes its region's state")
	_check(WS.region_of("winterfell") == "the_north", "Winterfell is in the North")
	_check(WS.state_of("beyond_wall") == "open", "a rule waits for its phase")

	var changes := []
	WS.state_changed.connect(func(id: String, s: String) -> void: changes.append([id, s]))
	GM.set_flag("act1_started")
	_check(WS.phase_id() == "hand_dies", "act1_started reaches the first phase")
	_check(WS.state_of("beyond_wall") == "sealed", "beyond the Wall is sealed")
	_check(not WS.can_enter("beyond_wall"), "a sealed region cannot be entered")
	_check(WS.state_of("the_vale") == "guarded", "the Vale watches the high road")
	_check(WS.state_of("castle_black") == "guarded", "a place's own rule applies")
	_check(changes.has(["beyond_wall", "sealed"]), "state_changed is emitted on change")
	_check(WS.reason_for("beyond_wall") != "", "a closed place gives a reason")
	_check(WS.reason_for("the_north") == "", "an open place gives none")

	GM.set_flag("act2_heard_jory_died")
	_check(WS.state_of("riverlands") == "contested", "the Riverlands burn after Tyrion is taken")
	_check(WS.can_enter("riverlands"), "contested can be entered, at a risk")
	_check(WS.state_of("the_vale") == "sealed", "the Bloody Gate is shut")
	_check(WS.state_of("riverrun") == "contested", "Riverrun follows its region before its own rule")

	GM.set_flag("act2_robert_died")
	_check(WS.state_of("kings_landing") == "guarded", "King's Landing is guarded after Robert dies")
	GM.set_flag("act3_heard_of_arrest")
	_check(WS.state_of("kings_landing") == "closed", "and closed after Ned's arrest")
	_check(not WS.can_enter("kings_landing"), "a closed city turns you back")
	_check(WS.state_of("rosby") == "guarded", "the rest of the Crownlands stays guarded")

	GM.set_flag("act3_banners_called")
	GM.set_flag("act3_moat_cailin")
	_check(WS.state_of("moat_cailin") == "sealed", "the host holds Moat Cailin")
	_check(WS.state_of("the_north") == "guarded", "the North is mustering")
	_check(WS.state_of("westerlands") == "closed", "the west is at war with the North")

	GM.flags.clear()
	GM.set_flag("act4_ned_arrested")
	_check(WS.state_of("kings_landing") == "closed", "any of a phase's flags reaches it")
	_check(WS.state_of("westerlands") == "guarded", "later phases are not reached by an earlier flag")

	print("WORLD %s (%d failure(s))" % ["PASS" if failures == 0 else "FAIL", failures])
	quit(1 if failures else 0)


func _check(ok: bool, what: String) -> void:
	print(("PASS  " if ok else "FAIL  ") + what)
	if not ok:
		failures += 1
