#version 330 core
out vec4 FragColor;

in vec3 TexCoords;
in float visibility;

uniform samplerCube skybox;
//uniform samplerCube skybox2;

uniform vec3 skyColor;
uniform float blend_factor;

const float lower_limit = 0.0;
const float upper_limit = 1.0;

void main()
{
    vec3 color = vec3(0.6, 0.78, 0.70);
    FragColor = texture(skybox, TexCoords);
//    FragColor2 = texture(skybox2, TexCoords);
//    final_color = mix(FragColor, FragColor2, blend_factor);

    // FragColor = mix(color, FragColor, visibility);

    float factor = (TexCoords.y - lower_limit) / (upper_limit - lower_limit);
    factor = clamp(factor, 0.0, 1.0);
    FragColor = mix(vec4(color, 1.0), FragColor, factor);

}