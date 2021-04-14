#version 330 core

uniform sampler2D diffuse_map;
in vec2 frag_tex_coords;

out vec4 out_color;

// Fog variable
in float visibility;

// Lighting effects variables (Unused)
//in vec3 surfaceNormal;
//in vec3 toLightVector;
//in vec3 toCameraVector;

void main() {
    vec4 color = vec4(0.6, 0.78, 0.70, 1);

    // Lighting effects for ground (Unused)
//    vec3 unitNormal = normalize(surfaceNormal);
//    vec3 unitLightVector = normalize(toLightVector);
//    float nDotl = dot(unitNormal, unitLightVector);
//    float brightness = max(nDotl, 0.2);
//    vec3 diffuse = brightness * vec3(color);

    out_color = texture(diffuse_map, frag_tex_coords);
    out_color = mix(color, out_color, visibility);
}
