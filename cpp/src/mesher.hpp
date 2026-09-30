#pragma once

#include <vector>

#include "ply_io.hpp"

// Connects neighbouring grid cells of one scanner into triangles.
// Triangles with an edge longer than maxEdge (mm) are skipped.
std::vector<Triangle> triangulateScanner(const std::vector<Point>& points, int scanner, float maxEdge);

// Removes points that are not part of any triangle and renumbers the triangles.
void removeUnusedPoints(std::vector<Point>& points, std::vector<Triangle>& triangles);

// Normal of each point = average direction of the triangles around it.
void computeNormals(std::vector<Point>& points, const std::vector<Triangle>& triangles);
