#version 330 core

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

// Lighting effects variables (Unused)
//out vec3 surfaceNormal;
//out vec3 toLightVector;
//out vec3 toCameraVector;


void main() {

    vec4 worldPosition = model * vec4(position, 1.0);
    vec4 positionRelativeToCam = view * worldPosition;

    gl_Position = projection * positionRelativeToCam;
    frag_tex_coords = texture_coords * 100;

    // Lighting effects for ground (Unused)
//    vec3 lightPosition = vec3(-1, -1, -1);
//    surfaceNormal = (model * vec4(normals, 0.0)).xyz;
//    toLightVector = lightPosition - worldPosition.xyz;
//    toCameraVector = (inverse(view) * vec4(0.0, 0.0, 0.0, 1.0)).xyz - worldPosition.xyz;

    float distance = length(positionRelativeToCam.xyz);
    visibility = exp(-pow((distance * density), gradient));
    visibility = clamp(visibility, 0.0, 1.0);
}
