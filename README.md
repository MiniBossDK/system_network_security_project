# ASCON vs AES-GCM on Arduino UNO R3

This repository contains code and the paper for an experimental comparison of ASCON-128 and AES-128-GCM on non-accelerated constrained hardware (Arduino UNO R3, ATmega328P @ 16 MHz).

## Structure
- `arduino/bench/` Arduino benchmark harness (C/C++ + libraries)
- `paper/` ACM LaTeX paper
- `data/raw/` raw serial logs and power traces (not committed)
- `data/processed/` processed CSV outputs (not committed)
- `scripts/` parsing + plotting scripts

## Current plan
1. Benchmark ASCON-128 and AES-128-GCM (software-only C implementations)
2. Measure execution time and energy per operation
3. Report results across multiple message sizes
