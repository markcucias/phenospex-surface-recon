#include "ply_io.hpp"

#include <algorithm>
#include <fstream>
#include <stdexcept>

#include "happly.h"

std::vector<Point> loadPoints(const std::string& path) {
    happly::PLYData ply(path);
    happly::Element& v = ply.getElement("vertex");

    std::string missing;
    for (std::string name : {"x", "y", "z", "scanner_id", "profile", "x_pos", "red", "green", "blue"}) {
        if (!v.hasProperty(name)) missing += " " + name;
    }
    if (!missing.empty()) {
        throw std::runtime_error("missing vertex properties:" + missing);
    }

    std::vector<float> x = v.getProperty<float>("x");
    std::vector<float> y = v.getProperty<float>("y");
    std::vector<float> z = v.getProperty<float>("z");
    std::vector<uint8_t> scanner = v.getProperty<uint8_t>("scanner_id");
    std::vector<uint32_t> profile = v.getProperty<uint32_t>("profile");
    std::vector<uint32_t> column = v.getProperty<uint32_t>("x_pos");
    std::vector<uint16_t> red = v.getProperty<uint16_t>("red");
    std::vector<uint16_t> green = v.getProperty<uint16_t>("green");
    std::vector<uint16_t> blue = v.getProperty<uint16_t>("blue");

    std::vector<Point> points(x.size());
    for (size_t i = 0; i < points.size(); ++i) {
        Point& p = points[i];
        p.x = x[i];
        p.y = y[i];
        p.z = z[i];
        p.scanner = scanner[i];
        p.profile = static_cast<int>(profile[i]);
        p.column = static_cast<int>(column[i]);
        p.red = red[i];
        p.green = green[i];
        p.blue = blue[i];
    }
    return points;
}

namespace {

template <typename T>
void writeBinary(std::ofstream& out, T value) {
    out.write(reinterpret_cast<const char*>(&value), sizeof(value));
}

// 99.9th percentile of all colour values; used as "full brightness" so a few bright spots
// don't make the whole mesh dark.
int colourScale(const std::vector<Point>& points) {
    if (points.empty()) return 1;
    std::vector<uint16_t> values;
    for (const Point& p : points) {
        values.push_back(p.red);
        values.push_back(p.green);
        values.push_back(p.blue);
    }
    std::sort(values.begin(), values.end());
    return std::max(1, static_cast<int>(values[values.size() * 999 / 1000]));
}

uint8_t toByte(uint16_t value, int scale) {
    return static_cast<uint8_t>(std::min(255, value * 255 / scale));
}

}  // namespace

void writeMesh(const std::string& path, const std::vector<Point>& points,
               const std::vector<Triangle>& triangles) {
    std::ofstream out(path, std::ios::binary);
    if (!out) {
        throw std::runtime_error("cannot write " + path);
    }

    out << "ply\n"
        << "format binary_little_endian 1.0\n"
        << "element vertex " << points.size() << "\n"
        << "property float x\n"
        << "property float y\n"
        << "property float z\n"
        << "property float nx\n"
        << "property float ny\n"
        << "property float nz\n"
        << "property uchar red\n"
        << "property uchar green\n"
        << "property uchar blue\n"
        << "element face " << triangles.size() << "\n"
        << "property list uchar int vertex_indices\n"
        << "end_header\n";

    const int scale = colourScale(points);
    for (const Point& p : points) {
        writeBinary(out, p.x);
        writeBinary(out, p.y);
        writeBinary(out, p.z);
        writeBinary(out, p.nx);
        writeBinary(out, p.ny);
        writeBinary(out, p.nz);
        writeBinary(out, toByte(p.red, scale));
        writeBinary(out, toByte(p.green, scale));
        writeBinary(out, toByte(p.blue, scale));
    }

    for (const Triangle& t : triangles) {
        writeBinary<uint8_t>(out, 3);
        writeBinary(out, t[0]);
        writeBinary(out, t[1]);
        writeBinary(out, t[2]);
    }
}
