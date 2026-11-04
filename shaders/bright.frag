#version 450 core

in vec2 vUV;
out vec4 fragColor;

uniform sampler2D uImage;
uniform float uThreshold;

void main()
{
    vec3 c = texture(uImage, vUV).rgb;
    // Keep only the part of each channel above the threshold.
    fragColor = vec4(max(c - vec3(uThreshold), vec3(0.0)), 1.0);
}