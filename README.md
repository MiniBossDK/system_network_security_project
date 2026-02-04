# ASCON vs AES-GCM on Arduino UNO R3

This repository contains code and the paper for an experimental comparison of AES-128-GCM, AES-256-GCM, ChaCha20-Poly1305 and ASCON128 on non-accelerated constrained hardware (Arduino UNO R3, ATmega328P @ 16 MHz).

## Structure
- `arduino/bench/` Arduino benchmark harness (C/C++ + libraries)
- `raw-data` raw serial logs and power traces
- `scripts/` parsing + plotting scripts
