#version 450 core

// One star = 7 floats: position (pc), color, absolute magnitude.
layout(location = 0) in vec3  aPosition;
layout(location = 1) in vec3  aColor;
layout(location = 2) in float aAbsMag;

uniform mat4  uView;
uniform mat4  uProjection;
uniform float uRefMag;      // apparent magnitude that maps to brightness 1.0
uniform float uPointScale;  // how much brighter stars grow in size

out vec3  vColor;
out float vFlux;

void main()
{
    vec4 viewPos = uView * vec4(aPosition, 1.0);

    // Distance from the camera in parsecs (clamped to avoid log10(0)).
    float d = max(length(viewPos.xyz), 0.01);

    // Apparent magnitude as seen from the camera:
    //   m = M + 5*log10(d) - 5
    float m = aAbsMag + 5.0 * log2(d) / log2(10.0) - 5.0;

    // Magnitudes are logarithmic: 5 magnitudes = factor of 100 in flux.
    float flux = pow(10.0, -0.4 * (m - uRefMag));
    flux = clamp(flux, 0.0, 8.0);

    vColor = aColor;
    vFlux  = flux;

    gl_PointSize = clamp(1.0 + uPointScale * sqrt(flux), 1.0, 24.0);
    gl_Position  = uProjection * viewPos;
}