// reconstruct: point cloud (PLY) -> triangle mesh (PLY)
//
// Current state: SKELETON. It loads the PlantEye PLY, prints what it found and writes the
// points back out, so the build / IO / timing path is proven before any algorithm is added.
// Pipeline stages are marked TODO and will be filled in step by step.
//
// Usage: reconstruct <input.ply> <output.ply>

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

#include "happly.h"
#include "timer.hpp"

namespace {

// One scanned point with the attributes we care about.
// Struct-of-arrays would be faster for some passes; array-of-structs is simpler to read for now.
struct Point {
    float x, y, z;
    uint8_t scanner_id;
    uint32_t profile;   // scan line index (sensor position along the travel axis)
    uint32_t x_pos;     // column along the laser line
    uint16_t red, green, blue, nir;
};

std::vector<Point> loadPoints(const std::string& path) {
    happly::PLYData ply(path);
    auto& v = ply.getElement("vertex");

    const std::vector<float> x = v.getProperty<float>("x");
    const std::vector<float> y = v.getProperty<float>("y");
    const std::vector<float> z = v.getProperty<float>("z");
    const std::vector<uint8_t> sid = v.getProperty<uint8_t>("scanner_id");
    const std::vector<uint32_t> prof = v.getProperty<uint32_t>("profile");
    const std::vector<uint32_t> xpos = v.getProperty<uint32_t>("x_pos");
    const std::vector<uint16_t> r = v.getProperty<uint16_t>("red");
    const std::vector<uint16_t> g = v.getProperty<uint16_t>("green");
    const std::vector<uint16_t> b = v.getProperty<uint16_t>("blue");
    const std::vector<uint16_t> nir = v.getProperty<uint16_t>("nir");

    std::vector<Point> pts(x.size());
    for (size_t i = 0; i < pts.size(); ++i) {
        pts[i] = {x[i], y[i], z[i], sid[i], prof[i], xpos[i], r[i], g[i], b[i], nir[i]};
    }
    return pts;
}

void printSummary(const std::vector<Point>& pts) {
    if (pts.empty()) { std::printf("no points\n"); return; }
    float minX = pts[0].x, maxX = pts[0].x, minY = pts[0].y, maxY = pts[0].y, minZ = pts[0].z, maxZ = pts[0].z;
    size_t perScanner[256] = {};
    for (const auto& p : pts) {
        minX = std::min(minX, p.x); maxX = std::max(maxX, p.x);
        minY = std::min(minY, p.y); maxY = std::max(maxY, p.y);
        minZ = std::min(minZ, p.z); maxZ = std::max(maxZ, p.z);
        ++perScanner[p.scanner_id];
    }
    std::printf("points: %zu\n", pts.size());
    std::printf("bbox x [%.1f, %.1f]  y [%.1f, %.1f]  z [%.1f, %.1f]\n", minX, maxX, minY, maxY, minZ, maxZ);
    for (int s = 0; s < 256; ++s)
        if (perScanner[s]) std::printf("scanner %d: %zu points\n", s, perScanner[s]);
}

// Temporary: writes points only (no faces) so the output path can be tested in CloudCompare.
void writePoints(const std::string& path, const std::vector<Point>& pts) {
    std::vector<std::array<double, 3>> pos(pts.size());
    std::vector<std::array<double, 3>> col(pts.size());
    for (size_t i = 0; i < pts.size(); ++i) {
        pos[i] = {pts[i].x, pts[i].y, pts[i].z};
        // 16-bit -> [0,1]; happly converts [0,1] doubles to 8-bit colors on write.
        col[i] = {pts[i].red / 65535.0, pts[i].green / 65535.0, pts[i].blue / 65535.0};
    }
    happly::PLYData out;
    out.addVertexPositions(pos);
    out.addVertexColors(col);
    out.write(path, happly::DataFormat::Binary);
}

}  // namespace

int main(int argc, char** argv) {
    if (argc < 3) {
        std::fprintf(stderr, "usage: %s <input.ply> <output.ply>\n", argv[0]);
        return 1;
    }
    const std::string inPath = argv[1];
    const std::string outPath = argv[2];

    try {
        ScopedTimer total("total");

        std::vector<Point> pts;
        {
            ScopedTimer t("load");
            pts = loadPoints(inPath);
        }
        printSummary(pts);

        // TODO stage 1: filtering / outlier removal
        // TODO stage 2: build per-scanner grid from (profile, x_pos)
        // TODO stage 3: triangulate grid with edge-length threshold
        // TODO stage 4: post-process (remove small components)
        // TODO stage 5: write mesh (vertices + faces + colors)

        {
            ScopedTimer t("write");
            writePoints(outPath, pts);
        }
        std::printf("wrote %s\n", outPath.c_str());
    } catch (const std::exception& e) {
        std::fprintf(stderr, "error: %s\n", e.what());
        return 1;
    }
    return 0;
}
