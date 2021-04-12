#version 330 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
layout(location = 0) in vec3 position;

out vec2 frag_tex_coords;

// fog variables
//const float density = 0.002;
//const float gradient = 1.5;
//out float visibility;

void main() {

    vec4 worldPosition = model * vec4(position, 1.0);
    vec4 positionRelativeToCam = view * worldPosition;

    gl_Position = projection * positionRelativeToCam;
    frag_tex_coords = position.xy;


//    float distance = length(positionRelativeToCam.xyz);
//    visibility = exp(-pow((distance * density), gradient));
//    visibility = clamp(visibility, 0.0, 1.0);
}
