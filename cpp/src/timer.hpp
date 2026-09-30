#pragma once
// Tiny scoped timer: prints how long a pipeline stage took when it goes out of scope.
//   { ScopedTimer t("load"); ...work... }   ->   [load] 1234.5 ms

#include <chrono>
#include <cstdio>
#include <string>
#include <utility>

class ScopedTimer {
public:
    explicit ScopedTimer(std::string name)
        : name_(std::move(name)), start_(std::chrono::steady_clock::now()) {}

    ~ScopedTimer() {
        const auto end = std::chrono::steady_clock::now();
        const double ms = std::chrono::duration<double, std::milli>(end - start_).count();
        std::printf("[%s] %.1f ms\n", name_.c_str(), ms);
    }

    ScopedTimer(const ScopedTimer&) = delete;
    ScopedTimer& operator=(const ScopedTimer&) = delete;

private:
    std::string name_;
    std::chrono::steady_clock::time_point start_;
};
