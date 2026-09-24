shader_type canvas_item;
// Plants sway in the wind: the top of the sprite leans, the base (where it meets
// the ground) stays put. Each plant's phase comes from its world position, so a
// wood ripples rather than every tree nodding in unison.

uniform float strength = 2.0;   // max lean at the top, in px
uniform float speed = 1.3;      // radians per second
uniform float gust = 0.35;      // extra slow, larger swell on top of the sway

varying float lean;

void vertex() {
	vec2 world = (MODEL_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xy;
	float phase = world.x * 0.013 + world.y * 0.007;
	float s = sin(TIME * speed + phase) + gust * sin(TIME * speed * 0.31 + phase * 0.5);
	// UV.y is 0 at the top of the texture and 1 at the bottom
	float h = 1.0 - UV.y;
	VERTEX.x += s * strength * h * h;
}
