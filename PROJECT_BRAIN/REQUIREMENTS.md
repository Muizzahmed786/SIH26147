# Requirements

## Functional Requirements
- Accept .IQ and .wav recordings.
- Signal parameter identification (sample rate, modulation, FEC, interleaving).
- Signal visualization (Waveform, Spectrum, Waterfall, Constellation).
- Demodulation (FSK, PSK, QAM).
- De-interleaving and FEC decoding.

## Non-Functional Requirements
- Evidence-driven and configurable UI.
- Maintain data provenance (metadata vs estimated).
- Backend processing decoupled from frontend via REST APIs.

## MVP Requirements
- .WAV, .IQ, .SigMF ingestion.
- Signal Visualization.
- Signal Characterization.
- Modulation Classification (BPSK, QPSK, 8PSK, 2FSK, 4FSK, GFSK, 16QAM).
- Demodulation (FSK, PSK, QAM).
- Bit Analysis.
- Recovery (Block de-interleaving, Viterbi, Reed-Solomon).
