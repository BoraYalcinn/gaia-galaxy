#pragma once

#include <GL/glew.h>

class Framebuffer{

    public:
        Framebuffer() = default;
        ~Framebuffer();
        Framebuffer(const Framebuffer&) = delete;
        Framebuffer& operator=(const Framebuffer&) = delete;

        void create(int width,int height);
        void destroy();

        void bind() const;

        GLuint colorTexture() const
        {
            return tex;
        }

        int width() const
        {
            return w;
        }

        int height() const
        {
            return h;
        }

    private:
        GLuint fbo;
        GLuint tex;    
        int h,w;

};