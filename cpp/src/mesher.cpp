#include "mesher.hpp"

#include <algorithm>
#include <climits>
#include <cmath>

namespace {

float distance(const Point& a, const Point& b) {
    return std::hypot(a.x - b.x, a.y - b.y, a.z - b.z);
}

// z of the triangle's normal: > 0 means it faces up.
float normalZ(const Point& a, const Point& b, const Point& c) {
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
}

}  // namespace

std::vector<Triangle> triangulateScanner(const std::vector<Point>& points, int scanner, float maxEdge) {
    std::vector<Triangle> triangles;

    int minRow = INT_MAX, maxRow = INT_MIN, minCol = INT_MAX, maxCol = INT_MIN;
    for (const Point& p : points) {
        if (p.scanner != scanner) continue;
        minRow = std::min(minRow, p.profile);
        maxRow = std::max(maxRow, p.profile);
        minCol = std::min(minCol, p.column);
        maxCol = std::max(maxCol, p.column);
    }
    if (maxRow < minRow) return triangles;

    const int rows = maxRow - minRow + 1;
    const int cols = maxCol - minCol + 1;

    // grid[row * cols + col] = index of the point in that cell, or -1 if empty
    std::vector<int> grid(rows * cols, -1);
    for (int i = 0; i < static_cast<int>(points.size()); ++i) {
        const Point& p = points[i];
        if (p.scanner == scanner) {
            grid[(p.profile - minRow) * cols + (p.column - minCol)] = i;
        }
    }

    for (int row = 0; row + 1 < rows; ++row) {
        for (int col = 0; col + 1 < cols; ++col) {
            // a b
            // c d
            int a = grid[row * cols + col];
            int b = grid[row * cols + col + 1];
            int c = grid[(row + 1) * cols + col];
            int d = grid[(row + 1) * cols + col + 1];

            for (Triangle t : {Triangle{a, c, b}, Triangle{b, c, d}}) {
                if (t[0] < 0 || t[1] < 0 || t[2] < 0) continue;

                const Point& p0 = points[t[0]];
                const Point& p1 = points[t[1]];
                const Point& p2 = points[t[2]];
                if (distance(p0, p1) < maxEdge && distance(p1, p2) < maxEdge && distance(p2, p0) < maxEdge) {
                    triangles.push_back(t);
                }
            }
        }
    }

    // The scanner looks down, so the surface should face up. If most triangles face down, flip them.
    double sum = 0;
    for (const Triangle& t : triangles) {
        sum += normalZ(points[t[0]], points[t[1]], points[t[2]]);
    }
    if (sum < 0) {
        for (Triangle& t : triangles) std::swap(t[1], t[2]);
    }

    return triangles;
}

void removeUnusedPoints(std::vector<Point>& points, std::vector<Triangle>& triangles) {
    std::vector<bool> used(points.size(), false);
    for (const Triangle& t : triangles) {
        for (int i : t) used[i] = true;
    }

    std::vector<Point> kept;
    std::vector<int> newIndex(points.size(), -1);
    for (size_t i = 0; i < points.size(); ++i) {
        if (used[i]) {
            newIndex[i] = static_cast<int>(kept.size());
            kept.push_back(points[i]);
        }
    }

    for (Triangle& t : triangles) {
        for (int& i : t) i = newIndex[i];
    }
    points = kept;
}

void computeNormals(std::vector<Point>& points, const std::vector<Triangle>& triangles) {
    for (const Triangle& t : triangles) {
        const Point& a = points[t[0]];
        const Point& b = points[t[1]];
        const Point& c = points[t[2]];

        // Cross product (b - a) x (c - a): perpendicular to the triangle, on its front side.
        float ux = b.x - a.x, uy = b.y - a.y, uz = b.z - a.z;
        float vx = c.x - a.x, vy = c.y - a.y, vz = c.z - a.z;
        float nx = uy * vz - uz * vy;
        float ny = uz * vx - ux * vz;
        float nz = ux * vy - uy * vx;

        for (int i : t) {
            points[i].nx += nx;
            points[i].ny += ny;
            points[i].nz += nz;
        }
    }

    for (Point& p : points) {
        float length = std::sqrt(p.nx * p.nx + p.ny * p.ny + p.nz * p.nz);
        if (length > 0) {
            p.nx /= length;
            p.ny /= length;
            p.nz /= length;
        }
    }
}
