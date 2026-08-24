#!/bin/bash
set -euo pipefail

echo "🌐 Installing C++ build essentials, CMake, testing libraries, and system Python packages..."
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    libgtest-dev \
    nlohmann-json3-dev \
    gcovr \
    python3-pytest \
    python3-pybind11

echo "🚀 Upgrading core Python packaging tools..."
python3 -m pip install --upgrade pip setuptools wheel

echo "📦 Installing solver dependencies from requirements.txt..."
python3 -m pip install -r requirements.txt

echo "⚙ Configuring and building all targets via CMake (with coverage enabled)..."
cmake -B build \
    -DCMAKE_BUILD_TYPE=Debug \
    -DENABLE_COVERAGE=ON

cmake --build build --parallel $(nproc)

echo "✅ Environment setup and CMake compilation completed successfully."
