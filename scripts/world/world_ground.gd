extends Node2D
## The ground of a large area, streamed in 1024 px chunks around the camera
## (docs/WORLD_DESIGN.md §7). Levels used to bake their ground into one PNG; the world
## is far too big for that, so it's painted into TileMapLayers as the player walks.
##
## `material_map` holds one pixel per 32 px grid *vertex*; its red channel is the
## material there (0 grass, 1 earth, 2 cobble, 3 snow). Each entry of `layers` is a
## corner-match tileset (tools/build_world_tilesets.py) drawn as its own TileMapLayer:
##   {"tileset": "res://...tres", "upper": [0], "only_near": []}
## A cell's corner is the tileset's upper surface when its vertex's material is in
## `upper`. A layer with `only_near` is drawn only on cells touching one of those
## materials (the cobbles of a yard over the grass/earth base).

const TILE := 32
const CHUNK := 32  ## cells per chunk side: 1024 px
const DECORATED_SHARE := 0.12

## Atlas coords for each set of upper corners (bit 1 TL, 2 TR, 4 BL, 8 BR), the same
## mapping as tools/build_ground.py's CORNERS_TO_ATLAS.
const ATLAS := {
	0: Vector2i(0, 3), 4: Vector2i(0, 0), 10: Vector2i(1, 0), 13: Vector2i(2, 0),
	12: Vector2i(3, 0), 9: Vector2i(0, 1), 14: Vector2i(1, 1), 15: Vector2i(2, 1),
	7: Vector2i(3, 1), 2: Vector2i(0, 2), 3: Vector2i(1, 2), 11: Vector2i(2, 2),
	5: Vector2i(3, 2), 8: Vector2i(1, 3), 6: Vector2i(2, 3), 1: Vector2i(3, 3),
}
const PLAIN := Vector2i(0, 4)

@export var material_map: Texture2D
@export var layers: Array[Dictionary] = []
## Chunks within this many of the camera's chunk are drawn; ones beyond it + 1 are cleared.
@export var radius: int = 1

var _img: Image
var _tilemaps: Array[TileMapLayer] = []
var _loaded: Dictionary = {}   ## Vector2i chunk -> true
var _size := Vector2i.ZERO     ## in cells
var _last := Vector2i(-99999, -99999)


func _ready() -> void:
	if material_map == null:
		return
	_img = material_map.get_image()
	_size = Vector2i(_img.get_width() - 1, _img.get_height() - 1)
	for spec in layers:
		var tm := TileMapLayer.new()
		tm.tile_set = load(String(spec["tileset"]))
		tm.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		add_child(tm)
		_tilemaps.append(tm)
	_update(true)


func _process(_delta: float) -> void:
	_update(false)


func loaded_chunks() -> Array:
	return _loaded.keys()


func size_in_cells() -> Vector2i:
	return _size


func _focus() -> Vector2:
	var cam := get_viewport().get_camera_2d()
	if cam != null:
		return cam.get_screen_center_position()
	var p := get_tree().get_first_node_in_group("player") as Node2D
	return p.global_position if p else global_position


func _update(force: bool) -> void:
	var local := to_local(_focus())
	var here := Vector2i(floori(local.x / (TILE * CHUNK)), floori(local.y / (TILE * CHUNK)))
	if here == _last and not force:
		return
	_last = here
	for key in _loaded.keys():
		if absi(key.x - here.x) > radius + 1 or absi(key.y - here.y) > radius + 1:
			_clear_chunk(key)
	for dy in range(-radius, radius + 1):
		for dx in range(-radius, radius + 1):
			var key := here + Vector2i(dx, dy)
			if not _loaded.has(key) and _in_map(key):
				_draw_chunk(key)


func _in_map(chunk: Vector2i) -> bool:
	return chunk.x >= 0 and chunk.y >= 0 and chunk.x * CHUNK < _size.x and chunk.y * CHUNK < _size.y


func _material(x: int, y: int) -> int:
	return int(round(_img.get_pixel(x, y).r * 255.0))


func _draw_chunk(chunk: Vector2i) -> void:
	_loaded[chunk] = true
	var x0 := chunk.x * CHUNK
	var y0 := chunk.y * CHUNK
	for cy in range(y0, mini(y0 + CHUNK, _size.y)):
		for cx in range(x0, mini(x0 + CHUNK, _size.x)):
			var m := [_material(cx, cy), _material(cx + 1, cy), _material(cx, cy + 1), _material(cx + 1, cy + 1)]
			for i in layers.size():
				var spec: Dictionary = layers[i]
				var near: Array = spec.get("only_near", [])
				if not near.is_empty() and not (m[0] in near or m[1] in near or m[2] in near or m[3] in near):
					continue
				var upper: Array = spec.get("upper", [0])
				var bits := 0
				for c in 4:
					if m[c] in upper:
						bits |= 1 << c
				var coords: Vector2i = ATLAS[bits]
				var alt := 0
				var h := _hash(cx, cy)
				if bits == 15 or bits == 0:
					alt = h % 8
					if bits == 15 and float((h >> 3) % 1000) / 1000.0 >= DECORATED_SHARE:
						coords = PLAIN
				_tilemaps[i].set_cell(Vector2i(cx, cy), 0, coords, alt)


func _clear_chunk(chunk: Vector2i) -> void:
	_loaded.erase(chunk)
	var x0 := chunk.x * CHUNK
	var y0 := chunk.y * CHUNK
	for tm in _tilemaps:
		for cy in range(y0, y0 + CHUNK):
			for cx in range(x0, x0 + CHUNK):
				tm.erase_cell(Vector2i(cx, cy))


static func _hash(x: int, y: int) -> int:
	var h := (x * 73856093) ^ (y * 19349663) ^ 0x5bd1e995
	h = (h ^ (h >> 13)) * 1274126177
	return (h ^ (h >> 16)) & 0x7fffffff
