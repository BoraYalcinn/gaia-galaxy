#pragma once

#include <string>
#include <vector>

constexpr int STAR_FLOATS = 7;
constexpr int STAR_BYTES = STAR_FLOATS * sizeof(float);

std::vector<float> loadStars(const std::string& path);