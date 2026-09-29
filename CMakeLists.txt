cmake_minimum_required(VERSION 3.16)
project(surface_recon LANGUAGES CXX)

# ---- Language / build defaults ---------------------------------------------
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)   # lets clangd / VS Code understand the project

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)   # geometry code is ~10x slower in Debug
endif()

# ---- Main executable --------------------------------------------------------
add_executable(reconstruct
  cpp/src/main.cpp
)

# happly is a single-header PLY reader/writer (MIT), vendored so the build needs no network.
target_include_directories(reconstruct PRIVATE third_party/happly cpp/src)

if(MSVC)
  target_compile_options(reconstruct PRIVATE /W4)
else()
  target_compile_options(reconstruct PRIVATE -Wall -Wextra -Wpedantic)
endif()
