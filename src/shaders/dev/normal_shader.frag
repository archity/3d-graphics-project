#version 330 core

// Interpolated values from the vertex shaders
in vec2 pass_textureCoordinates;
//in vec3 toLightVector[4];
in vec3 toCameraVector;
in float visibility;

// Ouput data
out vec4 color;

// Values that stay constant for the whole mesh.
uniform sampler2D DiffuseTextureSampler;
uniform sampler2D NormalTextureSampler;

uniform vec3 k_d;
uniform vec3 k_a;
uniform vec3 k_s;
uniform float s;
//uniform sampler2D SpecularTextureSampler;
//uniform mat4 V;
//uniform mat4 M;
//uniform mat3 MV3x3;
uniform vec3 LightPosition_worldspace;

void main(){

	vec3 LightColor = vec3(1,1,1);

	vec4 textureColour = texture(DiffuseTextureSampler, pass_textureCoordinates, -1.0);
	if(textureColour.a<0.5){
		discard;
	}
	color = textureColour;


}