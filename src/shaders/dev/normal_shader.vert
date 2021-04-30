#version 330 core

// Input vertex data, different for all executions of this shader.
layout(location = 0) in vec3 vertexPosition_modelspace;
layout(location = 1) in vec2 vertexUV;
layout(location = 2) in vec3 vertexNormal_modelspace;
layout(location = 3) in vec3 vertexTangent_modelspace;
layout(location = 4) in vec3 vertexBitangent_modelspace;

// Output data
out vec2 pass_textureCoordinates;
//out vec3 toLightVector[4];
out vec3 toCameraVector;
out float visibility;


// Values that stay constant for the whole mesh.
uniform mat4 MVP;
uniform mat4 V;
uniform mat4 M;
uniform mat4 P;
uniform mat3 MV3x3;
uniform vec3 LightPosition_worldspace;

const float density = 0;
const float gradient = 5.0;

void main(){

	vec4 worldPosition =  P * vec4(vertexPosition_modelspace, 1);
	mat4 modelViewMatrix = V * M;
	vec4 positionRelativeToCam = modelViewMatrix * vec4(vertexPosition_modelspace,1.0);
	gl_Position = P * positionRelativeToCam;

	pass_textureCoordinates = vertexUV;

	vec3 surfaceNormal = (modelViewMatrix * vec4(vertexNormal_modelspace, 0.0)).xyz;

	vec3 norm = normalize(surfaceNormal);
	vec3 tang = normalize((modelViewMatrix * vec4(vertexTangent_modelspace, 0.0)).xyz);
	vec3 bitang = normalize(cross(norm, tang));

	mat3 toTangentSpace = mat3(
		tang.x, bitang.x, norm.x,
		tang.y, bitang.y, norm.y,
		tang.z, bitang.z, norm.z
	);

	toCameraVector = toTangentSpace * (-positionRelativeToCam.xyz);
	float distance = length(positionRelativeToCam.xyz);
	visibility = exp(-pow((distance*density),gradient));
	visibility = clamp(visibility, 0.0, 1.0);

}

