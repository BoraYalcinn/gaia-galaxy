#include <GL/glew.h>     // must come before glfw3.h
#include <GLFW/glfw3.h>

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

#include <cmath>
#include <cstdio>
#include <vector>

#include "camera.h"
#include "framebuffer.h"
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

static void scrollCallback(GLFWwindow* /*window*/, double /*xoffset*/, double yoffset)
{
    // Each scroll step multiplies the speed by 1.2 (or divides when scrolling back).
    float speed = camera.getMoveSpeed() * std::pow(1.2f, static_cast<float>(yoffset));
    speed = glm::clamp(speed, 1.0f, 500000.0f);
    camera.setMoveSpeed(speed);
}

int main()
{
    // Load star data first (does not need OpenGL).
    std::vector<float> stars = loadStars("data/stars.bin");
    if (stars.empty()) {
        std::fprintf(stderr, "No stars loaded. Run the Python tools first.\n");
        return 1;
    }

    // The procedural galaxy layer is optional.
    std::vector<float> galaxy = loadStars("data/galaxy.bin");
    const bool hasGalaxy = !galaxy.empty();
    if (!hasGalaxy) {
        std::fprintf(stderr, "No galaxy layer loaded (run tools/generate_galaxy.py).\n");
    }

    const size_t gaiaCount   = stars.size() / STAR_FLOATS;
    const size_t galaxyCount = galaxy.size() / STAR_FLOATS;
    std::printf("Loaded %zu Gaia stars and %zu procedural stars\n", gaiaCount, galaxyCount);

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
    glfwSwapInterval(0);   

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
    glfwSetScrollCallback(window, scrollCallback);
    glfwSetCursorPosCallback(window, mouseCallback);
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);

    // Scope: Shader, Renderer and Framebuffer free their GL objects in their
    // destructors, which must run before the GL context is destroyed.
    {
        Shader shader;
        shader.CreateFromFile("shaders/stars.vert", "shaders/stars.frag");

        Renderer renderer;
        renderer.init(stars);

        Renderer galaxyRenderer;
        if (hasGalaxy) {
            galaxyRenderer.init(galaxy);
        }

        // Camera at the Sun, looking toward the galactic center (+X).
        // Positions are in parsecs, speed in parsecs per second.
        camera = Camera(glm::vec3(-8122.0f, 21.0f, 0.0f), glm::vec3(0.0f, 1.0f, 0.0f),
                        0.0f, 0.0f, 200.0f, 0.1f);

        // Additive blending: overlapping stars add up to brighter light.
        glEnable(GL_PROGRAM_POINT_SIZE);
        glEnable(GL_BLEND);
        glBlendFunc(GL_ONE, GL_ONE);
        glDisable(GL_DEPTH_TEST);

        int fbW, fbH;
        glfwGetFramebufferSize(window, &fbW, &fbH);

        Framebuffer hdr;
        hdr.create(fbW, fbH);
        Framebuffer bloomFbo[2];
        bloomFbo[0].create(fbW / 2, fbH / 2);
        bloomFbo[1].create(fbW / 2, fbH / 2);

        Shader composite;
        composite.CreateFromFile("shaders/fullscreen.vert", "shaders/composite.frag");

        Shader bright;
        bright.CreateFromFile("shaders/fullscreen.vert", "shaders/bright.frag");

        Shader blur;
        blur.CreateFromFile("shaders/fullscreen.vert", "shaders/blur.frag");

        GLuint emptyVao = 0;
        glGenVertexArrays(1, &emptyVao);   // core profile needs a VAO even with no vertex data

        // Tunable parameters (adjusted with the arrow keys or edited here).
        float refMag           = 16.0f;
        float exposure         = 1.0f;
        float bloomStrength    = 0.6f;
        float bloomThreshold   = 1.0f;
        const int blurPasses   = 5;
        float galaxyFluxScale  = 100.0f;

        // Timing and FPS counter.
        double lastTime  = glfwGetTime();
        double fpsTimer  = lastTime;
        int    frameCount = 0;

        while (!glfwWindowShouldClose(window)) {
            double now = glfwGetTime();
            float deltaTime = static_cast<float>(now - lastTime);
            lastTime = now;

            if (keys[GLFW_KEY_UP])    refMag   += 4.0f * deltaTime;
            if (keys[GLFW_KEY_DOWN])  refMag   -= 4.0f * deltaTime;
            if (keys[GLFW_KEY_RIGHT]) exposure *= 1.0f + 1.5f * deltaTime;
            if (keys[GLFW_KEY_LEFT])  exposure /= 1.0f + 1.5f * deltaTime;

            glfwPollEvents();
            camera.keyControl(keys, deltaTime);

            // --- Update the window title with live stats twice a second ---
            ++frameCount;
            if (now - fpsTimer >= 0.5) {
                double fps = frameCount / (now - fpsTimer);
                float distToCenter = glm::length(camera.getCameraPosition());

                char title[256];
                std::snprintf(title, sizeof(title),
                              "Gaia Galaxy | %.0f FPS (%.1f ms) | %zu stars (%zu Gaia + %zu procedural) | "
                              "speed %.0f pc/s | %.2f kpc from center | refMag %.1f | exposure %.2f",
                              fps, 1000.0 / fps,
                              gaiaCount + galaxyCount, gaiaCount, galaxyCount,
                              camera.getMoveSpeed(), distToCenter / 1000.0f,
                              refMag, exposure);
                glfwSetWindowTitle(window, title);

                fpsTimer   = now;
                frameCount = 0;
            }

            int w, h;
            glfwGetFramebufferSize(window, &w, &h);
            if (h == 0) continue;   // minimized

            if (w != hdr.width() || h != hdr.height()) {
                hdr.create(w, h);   // window was resized
                bloomFbo[0].create(w / 2, h / 2);
                bloomFbo[1].create(w / 2, h / 2);
            }

            // --- Pass 1: draw the stars into the HDR texture ---
            hdr.bind();
            glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
            glClear(GL_COLOR_BUFFER_BIT);

            glEnable(GL_BLEND);
            glBlendFunc(GL_ONE, GL_ONE);

            float aspect = static_cast<float>(w) / static_cast<float>(h);
            glm::mat4 projection = glm::perspective(glm::radians(60.0f), aspect, 1.0f, 100000000.0f);

            shader.UseShader();
            shader.SetMat4("uView", camera.calculateViewMatrix());
            shader.SetMat4("uProjection", projection);
            shader.SetFloat("uRefMag", refMag);

            // before drawing Gaia
            shader.SetFloat("uDistanceFalloff", 1.0f);
            // before drawing the procedural galaxy
            shader.SetFloat("uDistanceFalloff", 0.0f);

            // Layer 1: real Gaia stars.
            shader.SetFloat("uFluxScale", 1.0f);
            shader.SetFloat("uPointScale", 3.0f);
            renderer.draw();

            // Layer 2: procedural galaxy.
            if (hasGalaxy) {
                shader.SetFloat("uFluxScale", galaxyFluxScale);
                shader.SetFloat("uPointScale", 1.0f);
                galaxyRenderer.draw();
            }

            // --- Bloom: bright pass (HDR -> bloomFbo[0]) ---
            glDisable(GL_BLEND);
            glBindVertexArray(emptyVao);

            bloomFbo[0].bind();
            bright.UseShader();
            glActiveTexture(GL_TEXTURE0);
            glBindTexture(GL_TEXTURE_2D, hdr.colorTexture());
            bright.SetFloat("uThreshold", bloomThreshold);
            glDrawArrays(GL_TRIANGLES, 0, 3);

            // --- Bloom: blur, ping-pong between the two framebuffers ---
            blur.UseShader();
            glm::vec2 texel(1.0f / bloomFbo[0].width(), 1.0f / bloomFbo[0].height());
            for (int i = 0; i < blurPasses; ++i) {
                bloomFbo[1].bind();                                   // horizontal
                glBindTexture(GL_TEXTURE_2D, bloomFbo[0].colorTexture());
                blur.SetVec2("uDirection", glm::vec2(texel.x, 0.0f));
                glDrawArrays(GL_TRIANGLES, 0, 3);

                bloomFbo[0].bind();                                   // vertical
                glBindTexture(GL_TEXTURE_2D, bloomFbo[1].colorTexture());
                blur.SetVec2("uDirection", glm::vec2(0.0f, texel.y));
                glDrawArrays(GL_TRIANGLES, 0, 3);
            }
            glBindVertexArray(0);

            // --- Pass 2: composite HDR + bloom, tone map onto the screen ---
            glBindFramebuffer(GL_FRAMEBUFFER, 0);
            glViewport(0, 0, w, h);
            glDisable(GL_BLEND);
            glClear(GL_COLOR_BUFFER_BIT);

            composite.UseShader();
            composite.SetInt("uHdrTexture", 0);
            composite.SetInt("uBloomTexture", 1);
            composite.SetFloat("uExposure", exposure);
            composite.SetFloat("uBloomStrength", bloomStrength);

            // Layer 1: real Gaia stars (physical 1/d^2 falloff).
            shader.SetFloat("uDistanceFalloff", 1.0f);
            shader.SetFloat("uFluxScale", 1.0f);
            shader.SetFloat("uPointScale", 3.0f);
            renderer.draw();

            // Layer 2: procedural galaxy (flat brightness).
            if (hasGalaxy) {
                shader.SetFloat("uDistanceFalloff", 0.0f);
                shader.SetFloat("uFluxScale", galaxyFluxScale);
                shader.SetFloat("uPointScale", 1.0f);
                galaxyRenderer.draw();
            }

            glActiveTexture(GL_TEXTURE0);
            glBindTexture(GL_TEXTURE_2D, hdr.colorTexture());
            glActiveTexture(GL_TEXTURE1);
            glBindTexture(GL_TEXTURE_2D, bloomFbo[0].colorTexture());
            glActiveTexture(GL_TEXTURE0);

            glBindVertexArray(emptyVao);
            glDrawArrays(GL_TRIANGLES, 0, 3);
            glBindVertexArray(0);

            glfwSwapBuffers(window);
        }

        glDeleteVertexArrays(1, &emptyVao);
    }

    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}