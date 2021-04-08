#version 330 core

uniform sampler2D diffuse_map;
in vec2 frag_uv;

// fragment position and normal of the fragment, in WORLD coordinates
// (you can also compute in VIEW coordinates, your choice! rename variables)
in vec3 w_position, w_normal;   // in world coodinates

// light dir, in world coordinates
uniform vec3 light_dir;

// material properties
uniform vec3 k_d;
uniform vec3 k_a;
uniform vec3 k_s;
// uniform vec3 r;
uniform float s;

// world camera position
uniform vec3 w_camera_position;

out vec4 out_color;

void main() {
    
    vec3 n = normalize(w_normal);
    vec3 l = normalize(-light_dir);
    vec3 r = normalize(reflect(light_dir, n));
    vec3 v = normalize(w_camera_position - w_position);
    // float s = 10;

    // 1. The Lambertian model
    // out_color = vec4(k_d * max(0, dot(n, l)) * vec3(texture(diffuse_map, frag_uv)), 1);

    // 2. The Phong model
    out_color = vec4((k_a + k_d * max(0, dot(n, l)) + k_s * max(0, pow(dot(r, v), s))) * vec3(texture(diffuse_map, frag_uv)), 1);

    // 3. Point Light - TODO
    // out_color = vec4((k_a + (1/d*d) * (k_d * max(0, dot(n, l)) + k_s * max(0, pow(dot(r, v), s)))) * vec3(texture(diffuse_map, frag_uv)), 1);
}
