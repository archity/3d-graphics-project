#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 uvs;
layout(location = 2) in vec3 normal;

uniform mat4 model, view, projection;

// position and normal for the fragment shader, in WORLD coordinates
// (you can also compute in VIEW coordinates, your choice! rename variables)
out vec3 w_position, w_normal;   // in world coordinates
out vec2 frag_uv;
out float visibility;
out vec3 to_light_vector;
out vec3 surface_normal;

const float density = 0.007;
const float gradient = 1.5;
vec3 light_position = vec3(0, 0, 0);

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

    // w_normal = (model * vec4(normal, 0)).xyz;
    surface_normal = (model * vec4(normal, 0.0)).xyz;
    to_light_vector = light_position - worldPosition.xyz;

    float distance = length(positionRelativeToCam.xyz);
    visibility = exp(-pow((distance * density), gradient));
    visibility = clamp(visibility, 0.0, 1.0);
}
