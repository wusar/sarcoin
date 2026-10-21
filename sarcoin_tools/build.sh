#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
cmake -S . -B build -DBUILD_GUI=OFF -DBUILD_TESTS=OFF -DBUILD_BENCH=OFF \
  -DENABLE_IPC=OFF -DWITH_ZMQ=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build build --target bitcoind bitcoin-cli -j "${SARCOIN_BUILD_JOBS:-4}"
