#pragma once

#include <stdio.h>
#include <string.h>
#include <iostream>
#include <fstream>

#include <GL/glew.h>


class Shader{

    public:

        Shader();
        
        void CreateFromString(const char* vertexCode,const char* fragmentCode);
        void CreateFromFile(const char* vertexLocation,const char* fragmentLocation);

        std::string ReadFile(const char* fileLocation);

        GLuint shaderID = 0;

        void UseShader();
        void ClearShader();

        ~Shader();
    
    private:

        void CompileShader(const char* vertexCode, const char* fragmentCode);
	    void AddShader(GLuint theProgram, const char* shaderCode, GLenum shaderType);

};

