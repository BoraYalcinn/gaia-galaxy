#include "camera.h"


Camera::Camera(){}

Camera::Camera(glm::vec3 position,glm::vec3 up,GLfloat startYaw,GLfloat startPitch,GLfloat moveSpeed,GLfloat turnSpeed) 
                :  position(position), up(up), worldUp(up),yaw(startYaw),pitch(startPitch),moveSpeed(moveSpeed),turnSpeed(turnSpeed)
{
    this->front = glm::vec3(0.f,0.f,-1.f);
    this->Update();
}

void Camera::mouseControl(GLfloat xChange,GLfloat yChange)
{
    xChange *= turnSpeed;
    yChange *= turnSpeed;

    yaw += xChange;
    pitch += yChange;

    if (pitch > 89.0f)pitch = 89.0f;
	
	if (pitch < -89.0f)pitch = -89.0f;
	
	Update();
}

void Camera::keyControl(bool* keys,GLfloat deltaTime)
{
    GLfloat velocity = moveSpeed * deltaTime;
    if (keys[GLFW_KEY_W]) position += front * velocity;
	if (keys[GLFW_KEY_S]) position -= front * velocity;
	if (keys[GLFW_KEY_A]) position -= right * velocity;
	if (keys[GLFW_KEY_D]) position += right * velocity;
}

glm::mat4 Camera::calculateViewMatrix()
{
    return glm::lookAt(position,position+front,up);
}

glm::vec3 Camera::getCameraPosition()
{
    return position;
}

glm::vec3 Camera::getCameraDirection()
{
    return front;
}

void Camera::Update()
{
    front.x = cos(glm::radians(yaw)) * cos(glm::radians(pitch));
	front.y = sin(glm::radians(pitch));
	front.z = sin(glm::radians(yaw)) * cos(glm::radians(pitch));
	front = glm::normalize(front);
	right = glm::normalize(glm::cross(front, worldUp)); 
	up = glm::normalize(glm::cross(right,front));
}

Camera::~Camera(){}