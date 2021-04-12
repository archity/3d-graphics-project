#version 330 core
out vec4 FragColor;

in vec3 TexCoords;
in float visibility;

uniform samplerCube skybox;
uniform vec3 skyColor;

void main()
{
    vec4 color = vec4(0.5, 0.5, 0.5, 1);
    FragColor = texture(skybox, TexCoords);
    FragColor = mix(color, FragColor, visibility);
}