#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 uvs;
layout(location = 2) in vec3 normal;

uniform mat4 model, view, projection;

// position and normal for the fragment shader, in WORLD coordinates
// (you can also compute in VIEW coordinates, your choice! rename variables)
out vec3 w_position, w_normal;   // in world coordinates
out vec2 frag_uv;

void main() {
    gl_Position = projection * view * model * vec4(position, 1.0);
    frag_uv = vec2(uvs.x, uvs.y);

    // compute the vertex position and normal in world or view coordinates
    w_normal = (model * vec4(normal, 0)).xyz;
    w_position =  (model * vec4(position, 1)).xyz;
}
