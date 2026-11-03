#pragma once

#include <stdio.h>
#include <string>


#include <GL/glew.h>


class Shader{

    public:
        
        void CreateFromString(const char* vertexCode,const char* fragmentCode);
        void CreateFromFile(const char* vertexLocation,const char* fragmentLocation);

        std::string ReadFile(const char* fileLocation);


};

