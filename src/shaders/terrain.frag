#version 330 core

const int NUM_LIGHT_SRC = 3;

uniform sampler2D diffuse_map;
uniform sampler2D blue_texture;
uniform sampler2D red_texture;
uniform sampler2D blendmap;
uniform vec3 fog_colour;

in vec2 frag_tex_coords;

out vec4 out_color;

// Fog variable
in float visibility;
in vec3 to_light_vector[NUM_LIGHT_SRC];
uniform vec3 atten_factor[3];

// Lighting effects variables (Unused)
//in vec3 surfaceNormal;
//in vec3 toLightVector;
//in vec3 toCameraVector;

void main() {

    vec4 blend_map_color = texture(blendmap, frag_tex_coords);
    // Background texture colour (black)
    float back_texture_amount = 1 - (blend_map_color.r + blend_map_color.g + blend_map_color.b);
    vec2 tiled_coords = frag_tex_coords * 100;
    vec4 background_texture_colour = texture(diffuse_map, tiled_coords) * back_texture_amount;
    vec4 blue_texture_colour = texture(blue_texture, tiled_coords) * blend_map_color.b;
    vec4 red_texture_colour = texture(red_texture, tiled_coords) * blend_map_color.r;

    vec4 total_color = vec4(0.0);
    for(int i = 0; i < NUM_LIGHT_SRC; i++)
    {
        float d = length(to_light_vector[i]);
        float atten = (atten_factor[i].x) + (atten_factor[i].y * d) + (atten_factor[i].z * d * d);

        total_color = total_color + (1/atten) * (background_texture_colour + blue_texture_colour + red_texture_colour);
    }

    //vec4 total_color = (1/(total_atten)) * (background_texture_colour + blue_texture_colour + red_texture_colour);

    // vec4 total_color = (1/(atten_factor));

    out_color = total_color;
    out_color = mix(vec4(fog_colour, 1), out_color, visibility);
}
