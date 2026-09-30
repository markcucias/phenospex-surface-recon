#pragma once

#include <array>
#include <cstdint>
#include <string>
#include <vector>

struct Point {
    float x, y, z;
    float nx = 0, ny = 0, nz = 0;   // normal, filled in by computeNormals
    int scanner;
    int profile;   // grid row
    int column;    // grid column (x_pos in the file)
    uint16_t red, green, blue;
};

// Three indices into the points list.
using Triangle = std::array<int, 3>;

std::vector<Point> loadPoints(const std::string& path);

void writeMesh(const std::string& path, const std::vector<Point>& points,
               const std::vector<Triangle>& triangles);
