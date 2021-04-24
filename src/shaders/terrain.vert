#version 330 core

const int NUM_LIGHT_SRC = 3;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

// Terrain attributes
// (vertices, tex coordinates and normals)
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texture_coords;
layout(location = 2) in vec3 normals;

out vec2 frag_tex_coords;

// Fog variables
const float density = 0.010;
const float gradient = 1.0;
out float visibility;
out vec3 to_light_vector[NUM_LIGHT_SRC];

// Lighting effects variables (Unused)
//out vec3 surfaceNormal;
//out vec3 toLightVector;
//out vec3 toCameraVector;
uniform vec3 light_position[NUM_LIGHT_SRC];

void main() {

    vec4 worldPosition = model * vec4(position, 1.0);
    vec4 positionRelativeToCam = view * worldPosition;

    gl_Position = projection * positionRelativeToCam;
    frag_tex_coords = texture_coords;

    // Lighting effects for ground (Unused)
//    vec3 lightPosition = vec3(-1, -1, -1);
//    surfaceNormal = (model * vec4(normals, 0.0)).xyz;
//    toLightVector = lightPosition - worldPosition.xyz;
//    toCameraVector = (inverse(view) * vec4(0.0, 0.0, 0.0, 1.0)).xyz - worldPosition.xyz;

    for(int i = 0;i < NUM_LIGHT_SRC; i++)
    {
        to_light_vector[i] = light_position[i] - worldPosition.xyz;
    }

    float distance = length(positionRelativeToCam.xyz);
    visibility = exp(-pow((distance * density), gradient));
    visibility = clamp(visibility, 0.0, 1.0);
}
