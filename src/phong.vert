#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 uvs;
layout(location = 2) in vec3 normal;

uniform mat4 model, view, projection;
//uniform mat3 nit_matrix;

// position and normal for the fragment shader, in WORLD coordinates
// (you can also compute in VIEW coordinates, your choice! rename variables)
out vec3 w_position, w_normal;   // in world coordinates
out vec2 frag_uv;

void main() {
    vec4 w_position4 = model * vec4(position, 1.0);
    gl_Position = projection * view * w_position4;
    frag_uv = vec2(uvs.x, uvs.y);

    // compute the vertex position and normal in world or view coordinates
    w_position =  w_position4.xyz / w_position4.w;

    // fragment normal in world coordinates
    mat3 nit_matrix = transpose(inverse(mat3(model)));
    w_normal = normalize(nit_matrix * normal);

    // w_normal = (model * vec4(normal, 0)).xyz;
}
