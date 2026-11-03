#include "star_loader.h"

#include <cstdio>
#include <fstream>

std::vector<float> loadStars(const std::string& path)
{
    std::ifstream file(path, std::ios::binary | std::ios::ate);
    if (!file.is_open()) {
        std::printf("Failed to open star file: %s\n", path.c_str());
        return {};
    }
    const std::streamsize size = file.tellg();
    if (size <= 0 || size % STAR_BYTES != 0) {
        std::printf("Invalid star file size (%lld bytes): %s\n",
                    static_cast<long long>(size), path.c_str());
        return {};
    }

    file.seekg(0);

    std::vector<float> data(static_cast<size_t>(size) / sizeof(float));
    file.read(reinterpret_cast<char*>(data.data()), size);
    if (!file) {
        std::printf("Failed to read star file: %s\n", path.c_str());
        return {};
    }

    return data;
}