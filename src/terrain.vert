#version 330 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texture_coords;
layout(location = 2) in vec3 normals;

out vec2 frag_tex_coords;

// fog variables
const float density = 0.010;
const float gradient = 1.0;
out float visibility;

out vec3 surfaceNormal;
out vec3 toLightVector;
out vec3 toCameraVector;

//simple diffuse lighting
//vec3 calculateLighting(){
//    vec3 lightDirection = vec3(-1, -1, -1);
//    vec2 lightBias = vec2(1, 1);
//
//	vec3 normal = in_normal.xyz * 2.0 - 1.0;//required just because of the format the normals were stored in (0 - 1)
//	float brightness = max(dot(-lightDirection, normal), 0.0);
//	return (lightColour * lightBias.x) + (brightness * lightColour * lightBias.y);
//}

void main() {

    vec4 worldPosition = model * vec4(position, 1.0);
    vec4 positionRelativeToCam = view * worldPosition;

    gl_Position = projection * positionRelativeToCam;
    frag_tex_coords = texture_coords * 100;


//    vec3 lightPosition = vec3(-1, -1, -1);
//    surfaceNormal = (model * vec4(normals, 0.0)).xyz;
//    toLightVector = lightPosition - worldPosition.xyz;
//    toCameraVector = (inverse(view) * vec4(0.0, 0.0, 0.0, 1.0)).xyz - worldPosition.xyz;


    float distance = length(positionRelativeToCam.xyz);
    visibility = exp(-pow((distance * density), gradient));
    visibility = clamp(visibility, 0.0, 1.0);
}
