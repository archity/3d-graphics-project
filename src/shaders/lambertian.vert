#version 330 core

const int NUM_LIGHT_SRC = 4;

// Fog visibility variables
const float density = 0.007;
const float gradient = 1.5;

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 uvs;
layout(location = 2) in vec3 normal;

uniform vec3 light_position[NUM_LIGHT_SRC];
uniform mat4 model, view, projection;

// position and normal for the fragment shader, in WORLD coordinates
out vec3 w_position, w_normal;

out vec2 frag_uv;

out float visibility;
out vec3 to_light_vector[NUM_LIGHT_SRC];


void main() {

    vec4 worldPosition = model * vec4(position, 1.0);
    vec4 positionRelativeToCam = view * worldPosition;

    //vec4 w_position4 = model * vec4(position, 1.0);
    gl_Position = projection * positionRelativeToCam;
    frag_uv = vec2(uvs.x, uvs.y);

    // compute the vertex position and normal in world or view coordinates
    w_position =  worldPosition.xyz / worldPosition.w;

    // fragment normal in world coordinates
    mat3 nit_matrix = transpose(inverse(mat3(model)));
    w_normal = normalize(nit_matrix * normal);

    // Get the light for all lights' position
    for(int i = 0;i < NUM_LIGHT_SRC; i++)
    {
        to_light_vector[i] = light_position[i] - worldPosition.xyz;
    }

    float distance = length(positionRelativeToCam.xyz);
    visibility = exp(-pow((distance * density), gradient));
    visibility = clamp(visibility, 0.0, 1.0);
}
