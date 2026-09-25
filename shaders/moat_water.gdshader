shader_type canvas_item;
// Placeholder water for moats and pools until a water tileset is made (the kits,
// docs/WORLD_DESIGN.md §6): dark, still, with slow bands of light moving across it,
// quantised to a few shades so it sits with the pixel art.

uniform vec4 deep : source_color = vec4(0.16, 0.24, 0.30, 1.0);
uniform vec4 light : source_color = vec4(0.30, 0.42, 0.50, 1.0);
uniform float speed = 0.15;

varying vec2 world;

void vertex() {
	world = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

void fragment() {
	vec2 p = floor(world / 2.0);
	float w = sin(p.x * 0.07 + p.y * 0.19 + TIME * speed * 6.0) * 0.5 + 0.5;
	w *= sin(p.x * 0.013 - p.y * 0.05 - TIME * speed * 3.0) * 0.5 + 0.5;
	float band = step(0.78, w) * 0.6 + step(0.92, w) * 0.4;
	COLOR = mix(deep, light, band);
}
