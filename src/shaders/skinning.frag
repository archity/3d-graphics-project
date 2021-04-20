#version 330 core

// receiving interpolated color for fragment shader
in vec3 fragment_color;
in vec2 frag_uv;

// fragment position and normal of the fragment, in WORLD coordinates
in vec3 w_position, w_normal;

// world camera position
uniform vec3 w_camera_position;

// material properties
uniform vec3 k_d, k_a, k_s;
uniform float s;

uniform sampler2D diffuse_map;

// output fragment color for OpenGL
out vec4 out_color;

uniform vec3 fog_colour;
in float visibility;

void main() {
    vec3 n = normalize(w_normal);
    vec3 l = normalize(-vec3(-1, -1, -1));
    vec3 r = reflect(-l, n);
    vec3 v = normalize(w_camera_position - w_position);

    // 2. The Phong model
    vec3 diffuse_color = k_d * max(dot(n, l), 0) * vec3(texture(diffuse_map, frag_uv));
    vec3 specular_color = k_s * pow(max(dot(r, v), 0), s) * vec3(texture(diffuse_map, frag_uv));
    vec3 ambient_color = k_a * vec3(texture(diffuse_map, frag_uv));
    out_color = vec4(ambient_color, 1) + vec4(diffuse_color, 1) + vec4(specular_color, 1);

    out_color = mix(vec4(fog_colour, 1), out_color, visibility);
}
