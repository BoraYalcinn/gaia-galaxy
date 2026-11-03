#include <GL/glew.h>     // must come before glfw3.h
#include <GLFW/glfw3.h>

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

#include <cstdio>
#include <vector>

#include "camera.h"
#include "renderer.h"
#include "shader.h"
#include "star_loader.h"

// --- Input state (written by GLFW callbacks, read in the main loop) ---
static bool   keys[1024] = {};
static double lastX = 0.0;
static double lastY = 0.0;
static bool   firstMouse = true;
static Camera camera;

static void keyCallback(GLFWwindow* window, int key, int /*scancode*/, int action, int /*mods*/)
{
    if (key < 0 || key >= 1024) return;   // unknown key

    if (key == GLFW_KEY_ESCAPE && action == GLFW_PRESS) {
        glfwSetWindowShouldClose(window, GLFW_TRUE);
    }

    if (action == GLFW_PRESS)        keys[key] = true;
    else if (action == GLFW_RELEASE) keys[key] = false;
}

static void mouseCallback(GLFWwindow* /*window*/, double xpos, double ypos)
{
    // Avoid a big jump on the very first event.
    if (firstMouse) {
        lastX = xpos;
        lastY = ypos;
        firstMouse = false;
    }

    double xChange = xpos - lastX;
    double yChange = lastY - ypos;   // reversed: window y grows downward
    lastX = xpos;
    lastY = ypos;

    camera.mouseControl(static_cast<GLfloat>(xChange), static_cast<GLfloat>(yChange));
}

int main()
{
    // Load star data first (does not need OpenGL).
    std::vector<float> stars = loadStars("data/stars.bin");
    if (stars.empty()) {
        std::fprintf(stderr, "No stars loaded. Run the Python tools first.\n");
        return 1;
    }
    std::printf("Loaded %zu stars\n", stars.size() / STAR_FLOATS);

    // On a Wayland session GLEW (built for GLX) can fail to initialize,
    // so force the X11 backend (XWayland).
    glfwInitHint(GLFW_PLATFORM, GLFW_PLATFORM_X11);

    if (!glfwInit()) {
        std::fprintf(stderr, "Failed to init GLFW\n");
        return 1;
    }

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 5);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    GLFWwindow* window = glfwCreateWindow(1280, 720, "Gaia Galaxy", nullptr, nullptr);
    if (!window) {
        std::fprintf(stderr, "Failed to create window\n");
        glfwTerminate();
        return 1;
    }

    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);

    glewExperimental = GL_TRUE;
    if (GLenum err = glewInit(); err != GLEW_OK) {
        std::fprintf(stderr, "Failed to init GLEW: %s\n", glewGetErrorString(err));
        glfwDestroyWindow(window);
        glfwTerminate();
        return 1;
    }

    std::printf("OpenGL %s\n", glGetString(GL_VERSION));
    std::printf("GPU: %s\n", glGetString(GL_RENDERER));

    // Input setup.
    glfwSetKeyCallback(window, keyCallback);
    glfwSetCursorPosCallback(window, mouseCallback);
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);

    // Scope: Shader and Renderer free their GL objects in their destructors,
    // which must run before the GL context is destroyed.
    {
        Shader shader;
        shader.CreateFromFile("shaders/stars.vert", "shaders/stars.frag");

        Renderer renderer;
        renderer.init(stars);

        // Camera at the Sun, looking down -z. Speed is in parsecs per second.
        camera = Camera(glm::vec3(0.0f), glm::vec3(0.0f, 1.0f, 0.0f),
                        -90.0f, 0.0f, 200.0f, 0.1f);

        // Additive blending: overlapping stars add up to brighter light.
        glEnable(GL_PROGRAM_POINT_SIZE);
        glEnable(GL_BLEND);
        glBlendFunc(GL_ONE, GL_ONE);
        glDisable(GL_DEPTH_TEST);

        double lastTime = glfwGetTime();

        while (!glfwWindowShouldClose(window)) {
            double now = glfwGetTime();
            float deltaTime = static_cast<float>(now - lastTime);
            lastTime = now;

            glfwPollEvents();
            camera.keyControl(keys, deltaTime);

            int w, h;
            glfwGetFramebufferSize(window, &w, &h);
            if (h == 0) continue;   // minimized
            glViewport(0, 0, w, h);

            glClearColor(0.0f, 0.0f, 0.02f, 1.0f);
            glClear(GL_COLOR_BUFFER_BIT);

            float aspect = static_cast<float>(w) / static_cast<float>(h);
            glm::mat4 projection =
                glm::perspective(glm::radians(60.0f), aspect, 0.1f, 100000.0f);

            shader.UseShader();
            shader.SetMat4("uView", camera.calculateViewMatrix());
            shader.SetMat4("uProjection", projection);
            shader.SetFloat("uRefMag", 10.0f);
            shader.SetFloat("uPointScale", 3.0f);

            renderer.draw();

            glfwSwapBuffers(window);
        }
    }

    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}