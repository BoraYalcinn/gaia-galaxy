#version 450 core

in vec2 vUV;
out vec4 fragColor;

uniform sampler2D uImage;
uniform vec2 uDirection;   // (1/width, 0) for horizontal, (0, 1/height) for vertical

// 9-tap Gaussian (center + 4 on each side)
const float weights[5] = float[](0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);

void main()
{
    vec3 result = texture(uImage, vUV).rgb * weights[0];
    for (int i = 1; i < 5; ++i) {
        vec2 offset = uDirection * float(i);
        result += texture(uImage, vUV + offset).rgb * weights[i];
        result += texture(uImage, vUV - offset).rgb * weights[i];
    }
    fragColor = vec4(result, 1.0);
}