#version 330 core
layout (location = 0) in vec3 aPos;

out vec3 TexCoords;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

const float density = 1.007;
const float gradient = 1.5;

out float visibility;

void main()
{
    vec4 worldPosition = model * vec4(aPos, 0.0);
    vec4 positionRelativeToCam = view * worldPosition;

    TexCoords = aPos;
    vec4 pos = projection * positionRelativeToCam;

    // Normalization
    gl_Position = pos.xyww;

    float distance = length(positionRelativeToCam.xyz);
    visibility = exp(-pow((distance * density), gradient));
    visibility = clamp(visibility, 0.0, 1.0);
}