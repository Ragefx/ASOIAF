@tool
extends Node2D
## A stand-in for a building whose art isn't made yet (docs/WORLD_DESIGN.md §6: the
## building kits come after the layout). It draws a plain massing - roof or wall-top,
## a front face with stone courses, a door - at the building's real footprint and
## height, so the castle can be walked, lit and y-sorted before the kit exists.
##
## The origin is the middle of the footprint's south edge, like every prop, so it
## y-sorts against people. `footprint` is the plan size (what the collider covers);
## `height` is how tall the front face stands.

@export var footprint := Vector2(200, 120)
@export var height: float = 120.0
@export var round: bool = false
@export var roof_color := Color(0.33, 0.35, 0.40)
@export var wall_color := Color(0.52, 0.51, 0.49)
@export var door: bool = true
## Crenellations along the top edge (walls, towers) instead of a pitched roof ridge.
@export var battlements: bool = false


func _draw() -> void:
	var w := footprint.x
	var d := footprint.y
	var h := height
	var face_top := -h
	var roof := Rect2(-w / 2.0, -d - h, w, d)
	var shade := wall_color.darkened(0.25)
	if round:
		var r := w / 2.0
		# the drum: a rectangle face with a rounded top (the roof disc) and bottom
		draw_rect(Rect2(-r, -h - d / 2.0, w, h), wall_color)
		_ellipse(Vector2(0, -d / 2.0), r, d / 2.0, wall_color)
		_ellipse(Vector2(0, -h - d / 2.0), r, d / 2.0, roof_color)
		for i in range(1, int(h / 12.0)):
			draw_line(Vector2(-r, -d / 2.0 - i * 12.0), Vector2(r, -d / 2.0 - i * 12.0), shade, 1.0)
		if battlements:
			_crenels(-r, r, -h - d / 2.0)
	else:
		draw_rect(roof, roof_color)
		draw_rect(Rect2(-w / 2.0, face_top, w, h), wall_color)
		draw_rect(Rect2(-w / 2.0, face_top, w, 3), roof_color.darkened(0.3))
		for i in range(1, int(h / 12.0)):
			var y := face_top + i * 12.0
			draw_line(Vector2(-w / 2.0, y), Vector2(w / 2.0, y), shade, 1.0)
		if battlements:
			_crenels(-w / 2.0, w / 2.0, roof.position.y)
			_crenels(-w / 2.0, w / 2.0, face_top)
		else:
			draw_line(Vector2(-w / 2.0, roof.position.y + d / 2.0), Vector2(w / 2.0, roof.position.y + d / 2.0),
					roof_color.lightened(0.15), 2.0)
	if door and h >= 60:
		var dw := minf(28.0, w * 0.3)
		draw_rect(Rect2(-dw / 2.0, -54, dw, 54), Color(0.23, 0.16, 0.11))
	# ground contact shadow
	draw_rect(Rect2(-w / 2.0, -2, w, 4), Color(0, 0, 0, 0.25))


func _ellipse(c: Vector2, rx: float, ry: float, col: Color) -> void:
	var pts := PackedVector2Array()
	for i in 32:
		var a := TAU * i / 32.0
		pts.append(c + Vector2(cos(a) * rx, sin(a) * ry))
	draw_colored_polygon(pts, col)


func _crenels(x0: float, x1: float, y: float) -> void:
	var x := x0
	while x < x1 - 6:
		draw_rect(Rect2(x, y - 8, 8, 8), wall_color.lightened(0.08))
		x += 14
