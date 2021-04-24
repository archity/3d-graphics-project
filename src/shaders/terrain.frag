#version 330 core

uniform sampler2D diffuse_map;
uniform sampler2D blue_texture;
uniform sampler2D red_texture;
uniform sampler2D blendmap;
uniform vec3 fog_colour;

in vec2 frag_tex_coords;

out vec4 out_color;

// Fog variable
in float visibility;
in vec3 to_light_vector;

// Lighting effects variables (Unused)
//in vec3 surfaceNormal;
//in vec3 toLightVector;
//in vec3 toCameraVector;

void main() {

    float d = length(to_light_vector);
    float atten_factor = (0.4) + (0.005 * d) + (0.0005 * d * d);

    vec4 blend_map_color = texture(blendmap, frag_tex_coords);
    // Background texture colour (black)
    float back_texture_amount = 1 - (blend_map_color.r + blend_map_color.g + blend_map_color.b);
    vec2 tiled_coords = frag_tex_coords * 100;
    vec4 background_texture_colour = texture(diffuse_map, tiled_coords) * back_texture_amount;
    vec4 blue_texture_colour = texture(blue_texture, tiled_coords) * blend_map_color.b;
    vec4 red_texture_colour = texture(red_texture, tiled_coords) * blend_map_color.r;

    vec4 total_color = (1/(atten_factor)) * (background_texture_colour + blue_texture_colour + red_texture_colour);

    out_color = total_color;
    out_color = mix(vec4(fog_colour, 1), out_color, visibility);
}
