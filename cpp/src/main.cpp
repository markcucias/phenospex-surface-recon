#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <stdexcept>
#include <string>
#include <vector>

#include "mesher.hpp"
#include "ply_io.hpp"
#include "timer.hpp"

int main(int argc, char** argv) {
    std::string input, output;
    float maxEdge = 5.0f;

    try {
        for (int i = 1; i < argc; ++i) {
            std::string arg = argv[i];
            if (arg == "--max-edge") {
                maxEdge = i + 1 < argc ? std::atof(argv[++i]) : 0;
            } else if (input.empty()) {
                input = arg;
            } else if (output.empty()) {
                output = arg;
            } else {
                throw std::runtime_error("unexpected argument: " + arg);
            }
        }
        if (input.empty() || output.empty() || !(maxEdge > 0)) {
            std::fprintf(stderr, "usage: %s <input.ply> <output.ply> [--max-edge MM]\n", argv[0]);
            return 2;
        }
        if (!std::filesystem::is_regular_file(input)) {
            throw std::runtime_error("input file not found: " + input);
        }

        ScopedTimer total("total");

        std::vector<Point> points;
        {
            ScopedTimer t("load");
            points = loadPoints(input);
        }
        std::printf("loaded %zu points\n", points.size());

        std::vector<Triangle> triangles;
        {
            ScopedTimer t("triangulate");
            for (int scanner : {0, 1}) {
                std::vector<Triangle> part = triangulateScanner(points, scanner, maxEdge);
                std::printf("scanner %d: %zu triangles\n", scanner, part.size());
                triangles.insert(triangles.end(), part.begin(), part.end());
            }
        }

        const size_t before = points.size();
        removeUnusedPoints(points, triangles);
        std::printf("removed %zu points that are in no triangle\n", before - points.size());

        computeNormals(points, triangles);

        {
            ScopedTimer t("write");
            std::filesystem::path dir = std::filesystem::path(output).parent_path();
            if (!dir.empty()) std::filesystem::create_directories(dir);
            writeMesh(output, points, triangles);
        }
        std::printf("wrote %s: %zu vertices, %zu triangles\n", output.c_str(), points.size(), triangles.size());
    } catch (const std::exception& e) {
        std::fprintf(stderr, "error: %s\n", e.what());
        return 1;
    }
    return 0;
}
