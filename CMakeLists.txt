cmake_minimum_required(VERSION 3.20)
project(gaia_galaxy CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)  

# Use the modern GLVND OpenGL libraries (avoids a CMake warning).
set(OpenGL_GL_PREFERENCE GLVND)

find_package(OpenGL REQUIRED)
find_package(glfw3 REQUIRED)
find_package(GLEW REQUIRED)
find_package(glm REQUIRED)

# Pick up every .cpp under src/ automatically. CONFIGURE_DEPENDS makes the
# build re-run CMake when files are added or removed, so new sources also
# land in compile_commands.json without a manual reconfigure.
file(GLOB_RECURSE GAIA_SOURCES CONFIGURE_DEPENDS src/*.cpp)

add_executable(gaia_galaxy ${GAIA_SOURCES})

target_include_directories(gaia_galaxy PRIVATE src)

target_link_libraries(gaia_galaxy PRIVATE
    OpenGL::GL
    glfw
    GLEW::GLEW
    glm::glm
)

target_compile_options(gaia_galaxy PRIVATE -Wall -Wextra)