#include "framebuffer.h"

#include <cstdio>

Framebuffer::~Framebuffer()
{
    destroy();
}

void Framebuffer::destroy()
{
    if (tex != 0)
    { 
        glDeleteTextures(1, &tex);        
        tex = 0; 
    }
    if (fbo != 0)  
    { 
        glDeleteFramebuffers(1, &fbo);    
        fbo = 0; 
    }
}

void Framebuffer::create(int width,int height)
{
    destroy();
    w = width;
    h = height;

    glGenTextures(1, &tex);
    glBindTexture(GL_TEXTURE_2D, tex);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, w, h, 0, GL_RGBA, GL_FLOAT, nullptr);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

    glGenFramebuffers(1, &fbo);
    glBindFramebuffer(GL_FRAMEBUFFER, fbo);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex, 0);

    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) 
    {
        std::printf("Framebuffer is not complete!\n");
    }

    glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

void Framebuffer::bind() const
{
    glBindFramebuffer(GL_FRAMEBUFFER,fbo);
    glViewport(0,0,w,h);
}