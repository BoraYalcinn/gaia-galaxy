#version 450 core

in vec3  vColor;
in float vFlux;

out vec4 fragColor;

void main()
{
    // gl_PointCoord is (0..1, 0..1) across the point sprite.
    vec2 p = gl_PointCoord * 2.0 - 1.0;
    float r2 = dot(p, p);
    if (r2 > 1.0) discard;                 // round points

    float falloff = exp(-4.0 * r2);        // soft glow, bright center

    // Additive blending adds this to whatever is already on screen.
    fragColor = vec4(vColor * vFlux * falloff, 1.0);
}