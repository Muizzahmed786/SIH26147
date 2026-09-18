# Architecture Decision Log

## ADR-001 — Hybrid DSP + ML Architecture
Date: 2026-09-18
Status: Accepted
Context: Need to analyze unknown RF signals.
Decision: Use mature DSP libraries for deterministic processing and ML exclusively for classification tasks where heuristics fail.
Reason: Prevents black-box AI from hallucinating signal parameters.

## ADR-002 — Python/FastAPI Backend & React/Vite Frontend
Date: 2026-09-18
Status: Accepted
Context: UI and processing architecture.
Decision: Use Vite + React + Vanilla CSS for a dynamic UI and FastAPI for high-performance Python DSP.
