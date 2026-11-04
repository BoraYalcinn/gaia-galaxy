#version 450 core

in vec2 vUV;
out vec4 fragColor;

uniform sampler2D uHdrTexture;   // unit 0 by default
uniform float uExposure;

// ACES filmic curve (Narkowicz approximation): compresses HDR into 0..1.
vec3 tonemapACES(vec3 x)
{
    const float a = 2.51;
    const float b = 0.03;
    const float c = 2.43;
    const float d = 0.59;
    const float e = 0.14;
    return clamp((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0);
}

void main()
{
    vec3 hdr = texture(uHdrTexture, vUV).rgb;
    vec3 mapped = tonemapACES(hdr * uExposure);
    mapped = pow(mapped, vec3(1.0 / 2.2));     // linear -> display gamma
    fragColor = vec4(mapped, 1.0);
}