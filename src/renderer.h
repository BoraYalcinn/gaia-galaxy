#pragma once

#include <GL/glew.h>
#include <glm/glm.hpp>
#include <vector>

class Renderer {
public:
    Renderer() = default;
    ~Renderer();
    Renderer(const Renderer&) = delete;
    Renderer& operator=(const Renderer&) = delete;

    // Uploads the star floats (7 per star) to the GPU. Needs a live GL context.
    void init(const std::vector<float>& stars);

    // Draws all stars as points.
    void draw();

private:
    GLuint vao = 0;
    GLuint vbo = 0;
    GLsizei starCount = 0;
};