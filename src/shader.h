#pragma once

#include <stdio.h>
#include <string.h>
#include <iostream>
#include <fstream>

#include <glm/gtc/type_ptr.hpp>
#include <GL/glew.h>     
#include <glm/glm.hpp>
#include <GLFW/glfw3.h>
#include <glm/gtc/matrix_transform.hpp>


class Shader{

    public:

        Shader();
        
        void CreateFromString(const char* vertexCode,const char* fragmentCode);
        void CreateFromFile(const char* vertexLocation,const char* fragmentLocation);
        void SetFloat(const char* name, float value);
        void SetMat4(const char* name, const glm::mat4& value);
        
        std::string ReadFile(const char* fileLocation);

        GLuint shaderID = 0;

        void UseShader();
        void ClearShader();

        ~Shader();
    
    private:

        void CompileShader(const char* vertexCode, const char* fragmentCode);
	    void AddShader(GLuint theProgram, const char* shaderCode, GLenum shaderType);

};

