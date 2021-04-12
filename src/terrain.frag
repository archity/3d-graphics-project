#version 330 core

uniform sampler2D diffuse_map;
in vec2 frag_tex_coords;

out vec4 out_color;

in float visibility;
uniform vec3 skyColor;

void main() {
//    vec4 color = vec4(0.5, 0.5, 0.5, 1);
    out_color = texture(diffuse_map, frag_tex_coords);
//    out_color = mix(color, out_color, visibility);
}
