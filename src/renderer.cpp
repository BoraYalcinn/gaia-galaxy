#include "renderer.h"

namespace 
{
    constexpr GLsizei FLOATS_PER_STAR = 7;
    constexpr GLsizei STRIDE = FLOATS_PER_STAR * sizeof(float);   // 28 bytes
}

Renderer::~Renderer()
{
    if(vbo != 0)glDeleteBuffers(1,&vbo);
    if(vao != 0)glDeleteBuffers(1,&vao);
}

Renderer::Renderer(const Renderer&) = delete;

void Renderer::init(const std::vector<float>& stars)
{
    starCount = static_cast<GLsizei>(stars.size() / FLOATS_PER_STAR);

    glGenVertexArrays(1,&vao);
    glBindVertexArray(vao);

    glGenBuffers(1,&vbo);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, stars.size() * sizeof(float) , stars.data(), GL_STATIC_DRAW);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, STRIDE,
                          reinterpret_cast<void*>(0));
    glEnableVertexAttribArray(0);

    // location 1: color (r, g, b), starts at byte 12
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, STRIDE, reinterpret_cast<void*>(3 * sizeof(float)));
    glEnableVertexAttribArray(1);

    // location 2: absolute magnitude, starts at byte 24
    glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, STRIDE, reinterpret_cast<void*>(6 * sizeof(float)));
    glEnableVertexAttribArray(2);

    glBindVertexArray(0);
}

void Renderer::draw()
{
    glBindVertexArray(vao);
    glDrawArrays(GL_POINTS, 0, starCount);
    glBindVertexArray(0);
}