# Architecture

## End-to-End System
ANALYST GUI (Vite/React) -> FASTAPI API -> Pipeline Manager -> Ingestion -> DSP / ML -> DSP Verification -> Synchronization -> Demodulation -> Bit Stream -> Correlation / Recovery -> Validation -> Report.

## Critical Architecture Rule
Do not implement DSP algorithms unnecessarily from scratch. Use NumPy, SciPy.

## DSP / ML Separation
- Classical DSP: FFT, PSD, SNR, Bandwidth, Synchronization, Demodulation.
- ML: Modulation Classification.
- Hypothesis Engine: FEC candidate generation.
