#include <GL/glew.h>     // must come before glfw3.h
#include <GLFW/glfw3.h>

#include "star_loader.h"

#include <vector>
#include <cstdio>

int main(){

    std::vector<float> stars = loadStars("data/stars.bin");
    std::printf("Loaded %zu stars\n", stars.size() / STAR_FLOATS);

    glfwInitHint(GLFW_PLATFORM,GLFW_PLATFORM_X11);

    if(!glfwInit()){
        std::fprintf(stderr,"Failed to init GLFW\n");
        return 1;
    }

    std::printf("GPU: %s\n", glGetString(GL_RENDERER));
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 5);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    GLFWwindow* window = glfwCreateWindow(1280,720,"Gaia Galaxy",nullptr,nullptr);
    if(!window){
        std::fprintf(stderr,"Failed to create window\n");
        glfwTerminate();
        return 1;
    }

    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);

    glewExperimental = GL_TRUE;
    if(GLenum err = glewInit(); err != GLEW_OK){
        std::fprintf(stderr,"Failed to init GLEW: %s\n",glewGetErrorString(err));
        glfwDestroyWindow(window);
        glfwTerminate();
        return 1;
    }

    std::printf("OpenGL %s\n",glGetString(GL_VERSION));

    while(!glfwWindowShouldClose(window)){
        int w,h;
        glfwGetFramebufferSize(window,&w,&h);
        glViewport(0,0,w,h);
        glClearColor(0.02f,0.02f,0.06f,1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}
