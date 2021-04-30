#version 330 core

const int NUM_LIGHT_SRC = 4;

uniform sampler2D diffuse_map;
in vec2 frag_uv;

// fragment position and normal of the fragment, in WORLD coordinates
in vec3 w_position, w_normal;
in float visibility;
in vec3 to_light_vector[NUM_LIGHT_SRC];

// material properties
uniform vec3 k_d;
uniform vec3 k_a;
uniform vec3 k_s;
uniform float s;

// Fog and light properties
uniform vec3 fog_colour;
uniform vec3 atten_factor[NUM_LIGHT_SRC];

// world camera position
uniform vec3 w_camera_position;

out vec4 out_color;


void main() {

    vec3 n = normalize(w_normal);
    vec3 v = normalize(w_camera_position - w_position);

    vec3 total_diffuse = vec3(0.0);
    vec3 total_specular = vec3(0.0);

    for(int i = 0; i < NUM_LIGHT_SRC; i++)
    {
        float d = length(to_light_vector[i]);

        // 2nd order equation for calculating attenuation factor based on distance
        float atten = (atten_factor[i].x) + (atten_factor[i].y * d) + (atten_factor[i].z * d * d);

        vec3 unit_light_vector = normalize(to_light_vector[i]);
        vec3 r = reflect(-unit_light_vector, n);

        // The Phong model parameters
        vec3 diffuse_color = k_d * max(dot(n, unit_light_vector), 0) * vec3(texture(diffuse_map, frag_uv));
        vec3 specular_color = k_s * pow(max(dot(r, v), 0), s) * vec3(texture(diffuse_map, frag_uv));

        // Point Light
        total_diffuse = total_diffuse + diffuse_color / (atten);
        total_specular = total_specular + specular_color / (atten);
    }
    // Ambient part outside loop since it's not light dependent
    vec3 ambient_color = k_a * vec3(texture(diffuse_map, frag_uv));

    out_color = vec4(ambient_color, 1) + (vec4(total_diffuse, 1) + vec4(total_specular, 1));
    out_color = mix(vec4(fog_colour, 1), out_color, visibility);

}
