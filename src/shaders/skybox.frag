#version 330 core
out vec4 FragColor;

in vec3 TexCoords;
in float visibility;

uniform samplerCube skybox;
uniform samplerCube skybox2;

uniform vec3 sky_color;
uniform float blend_factor;

const float lower_limit = 0.0;
const float upper_limit = 1.4;

void main()
{
    // float blend_factor = 0.5;
    // vec4 color = vec4(0.6, 0.70, 0.70, 1.0);
    vec4 color = vec4(0.2, 0.20, 0.20, 1.0);
    vec4 tex1 = texture(skybox, TexCoords);
    vec4 tex2 = texture(skybox2, TexCoords);
    vec4 final_color = mix(tex1, tex2, blend_factor);

    float factor = (TexCoords.y - lower_limit) / (upper_limit - lower_limit);
    factor = clamp(factor, 0.0, 1.0);
    FragColor = mix(vec4(sky_color, 1), final_color, factor);

    FragColor = mix(FragColor, vec4(sky_color, 1), visibility);

}