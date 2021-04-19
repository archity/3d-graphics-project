#version 330 core

uniform sampler2D diffuse_map;
uniform sampler2D blue_texture;
uniform sampler2D blendmap;
uniform vec3 fog_colour;

in vec2 frag_tex_coords;

out vec4 out_color;

// Fog variable
in float visibility;

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

    vec4 total_color = background_texture_colour + blue_texture_colour;

    // vec4 color = vec4(0.2, 0.20, 0.20, 1.0);

    // Lighting effects for ground (Unused)
//    vec3 unitNormal = normalize(surfaceNormal);
//    vec3 unitLightVector = normalize(toLightVector);
//    float nDotl = dot(unitNormal, unitLightVector);
//    float brightness = max(nDotl, 0.2);
//    vec3 diffuse = brightness * vec3(color);

    out_color = total_color;
    out_color = mix(vec4(fog_colour, 1), out_color, visibility);
}
