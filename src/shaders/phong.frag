#version 330 core

uniform sampler2D diffuse_map;
in vec2 frag_uv;

// fragment position and normal of the fragment, in WORLD coordinates
// (you can also compute in VIEW coordinates, your choice! rename variables)
in vec3 w_position, w_normal;   // in world coodinates

// light dir, in world coordinates
//uniform vec3 light_dir;

// material properties
uniform vec3 k_d;
uniform vec3 k_a;
uniform vec3 k_s;
//// uniform vec3 r;
uniform float s;
uniform vec3 fog_colour;

// world camera position
uniform vec3 w_camera_position;

out vec4 out_color;

in vec3 surface_normal;
in vec3 to_light_vector;
in float visibility;
uniform vec3 skyColor;

void main() {

    // vec4 color = vec4(0.2, 0.20, 0.20, 1.0);

    float d = length(to_light_vector);
    float atten_factor = (0.4) + (0.005 * d) + (0.0005 * d * d);
    vec3 unit_light_vector = normalize(to_light_vector);
    vec3 unit_normal = normalize(surface_normal);

    vec3 n = normalize(w_normal);
    vec3 l = normalize(-vec3(-1, -1, -1));
    vec3 r = reflect(-l, n);
    vec3 v = normalize(w_camera_position - w_position);


    // 1. The Lambertian model
    //out_color = vec4(k_d * max(0, dot(n, l)) * vec3(texture(diffuse_map, frag_uv)), 1);

    // 2. The Phong model
    vec3 diffuse_color = k_d * max(dot(n, unit_light_vector), 0) * vec3(texture(diffuse_map, frag_uv));
    vec3 specular_color = k_s * pow(max(dot(r, v), 0), s) * vec3(texture(diffuse_map, frag_uv));
    vec3 ambient_color = k_a * vec3(texture(diffuse_map, frag_uv));
    // out_color = vec4(ambient_color, 1) + vec4(diffuse_color, 1) + vec4(specular_color, 1);

    //vec3(texture(diffuse_map, frag_uv))

    // 3. Point Light
    out_color = vec4(ambient_color, 1) + (1/(atten_factor)) * (vec4(diffuse_color, 1) + vec4(specular_color, 1));
    // out_color = (1/(atten_factor)) * (vec4(diffuse_color, 1));

    out_color = mix(vec4(fog_colour, 1), out_color, visibility);
}
