# SIH26147 --- Automated RF Signal Analysis & Recovery Platform

**Technical Product Requirements Document (PRD)**\
**Problem Statement:** SIH26147\
**Organization:** National Technical Research Organisation (NTRO)\
**Category:** Software / Space Technology\
**Status:** MVP Definition\
**Version:** 1.0\
**Date:** 18 September 2026

------------------------------------------------------------------------

## 1. Executive Summary

SIH26147 asks for a GUI-based system that can ingest `.IQ` and `.wav`
recordings and automate signal analysis, parameter extraction,
demodulation, de-interleaving, FEC processing, and bit-stream
correlation.

The complete problem statement is intentionally broad. The MVP therefore
focuses on a technically defensible end-to-end pipeline rather than
attempting universal signal intelligence.

### MVP objective

Build an **analyst-oriented RF Signal Analysis & Recovery Platform**
that:

1.  Ingests `.wav`, raw `.iq`, and metadata-described SigMF recordings.
2.  Normalizes recordings into a common internal representation.
3.  Visualizes waveform, spectrum/PSD, waterfall, and constellation
    data.
4.  Extracts measurable signal characteristics such as bandwidth, SNR,
    dominant frequency and estimated symbol rate where possible.
5.  Automatically classifies a defined set of digital modulations.
6.  Demodulates supported FSK, PSK and QAM signals.
7.  Produces a recovered bit stream.
8.  Performs bit-stream correlation and repeated-pattern/preamble
    analysis.
9.  Supports selected de-interleaving and FEC recovery.
10. Reports confidence, evidence and failure reasons instead of
    presenting uncertain inferences as facts.
11. Allows an analyst to inspect and manually override processing
    parameters.

The MVP is **not** intended to automatically decode every arbitrary
terrestrial signal or uniquely infer every FEC/interleaver configuration
from signal samples alone.

------------------------------------------------------------------------

# 2. Problem Context

The SIH statement describes raw terrestrial signal recordings in HF, VHF
and UHF bands, collected by different sensors and at different
locations. Recordings may be stored as `.wav` or `.IQ`, and metadata may
be incomplete. The requested system should improve signal visibility and
automate extraction of parameters including sampling frequency,
modulation, FEC and interleaving, followed by demodulation,
de-interleaving, FEC processing and bit-stream correlation.

The target workflow is therefore:

``` text
Raw Recording
     |
     v
Ingestion + Metadata
     |
     v
Signal Characterization
     |
     +--> Spectrum / PSD
     +--> Waterfall
     +--> Bandwidth
     +--> SNR
     +--> Frequency characteristics
     +--> Symbol-rate estimation
     |
     v
Modulation Classification
     |
     v
Synchronization + Demodulation
     |
     v
Recovered Symbols / Bits
     |
     +--> Bit-stream correlation
     +--> Pattern / preamble analysis
     |
     v
De-interleaving / FEC hypotheses
     |
     v
Validation
     |
     v
Analyst Report + Export
```

------------------------------------------------------------------------

# 3. Product Vision

### Product statement

> Transform raw RF recordings into an evidence-backed signal analysis
> report and, where the signal is supported, a recoverable bit stream
> through a combination of classical DSP, machine learning and
> configurable decoding pipelines.

### Design principle

**DSP first, ML where classification benefits from learning, and
hypothesis-driven recovery where parameters cannot be known directly.**

The system should never hide uncertainty behind a single black-box
answer.

------------------------------------------------------------------------

# 4. Goals

## 4.1 Primary Goals

-   Provide a single GUI for `.wav` and `.IQ` signal analysis.
-   Normalize different recording formats into a common signal
    representation.
-   Make signal characteristics visually inspectable.
-   Automate classification of a defined modulation set.
-   Provide reliable demodulation for the supported modulation families.
-   Produce a usable bit stream from supported signals.
-   Provide bit-stream correlation and repeated-pattern detection.
-   Implement a limited but credible FEC/de-interleaving recovery layer.
-   Expose confidence and evidence for automated results.
-   Allow manual analyst intervention.
-   Provide reproducible analysis results and exportable reports.

## 4.2 Secondary Goals

-   Support large recordings through windowing/chunking.
-   Preserve source metadata and processing provenance.
-   Provide benchmark metrics for classification and decoding.
-   Make the processing engine independently testable from the GUI.

------------------------------------------------------------------------

# 5. Non-Goals

The following are explicitly outside the MVP:

-   Universal modulation classification.
-   Guaranteed identification of unknown protocols.
-   Guaranteed recovery from arbitrary low-SNR recordings.
-   Universal automatic FEC identification.
-   Universal automatic interleaver identification.
-   Full protocol reverse engineering.
-   Live RF capture from SDR hardware.
-   Real-time streaming analysis.
-   Spectrum monitoring across multiple physical sensors.
-   Automatic interpretation of recovered payloads.
-   Cryptographic decryption.
-   Classification of arbitrary proprietary waveforms without training
    or engineering support.
-   Building every FEC/interleaver implementation from scratch.

These can be future extensions.

------------------------------------------------------------------------

# 6. MVP Scope

## 6.1 Input Formats

### Required

#### WAV

Support:

-   Mono WAV.
-   PCM integer samples.
-   Floating-point samples where practical.
-   Real-valued recordings.
-   Complex IQ encoded in an agreed application convention where
    applicable.

The parser must expose:

``` text
sample_rate
sample_width
channels
duration
sample_count
dtype
```

#### Raw IQ

Support an explicitly defined set of common encodings for the demo:

``` text
complex64
float32 IQ
int16 IQ
uint8 IQ
```

The UI must ask for missing information when raw IQ does not contain
metadata:

``` text
Sample rate
Center frequency (optional)
IQ format
Byte order
Signed/unsigned
I/Q ordering
```

### Recommended

#### SigMF

Treat SigMF as a metadata-aware input format when a `.sigmf-meta` file
is supplied alongside signal data.

------------------------------------------------------------------------

# 7. Internal Signal Representation

All input formats must be converted to a canonical object.

``` python
SignalRecord:
    id
    source_file
    source_format

    samples
    dtype
    sample_count

    sample_rate
    center_frequency
    bandwidth

    channels
    duration

    metadata
    metadata_source

    analysis_status
```

### Metadata provenance

Every important parameter must record its source:

``` text
source:
    metadata
    user_input
    estimated
    derived
    unknown
```

Example:

``` json
{
  "sample_rate": {
    "value": 2400000,
    "unit": "S/s",
    "source": "metadata",
    "confidence": 1.0
  },
  "symbol_rate": {
    "value": 250000,
    "unit": "symbols/s",
    "source": "estimated",
    "confidence": 0.87
  }
}
```

------------------------------------------------------------------------

# 8. Signal Processing Pipeline

## 8.1 Stage 1 --- Ingestion

``` text
File
 |
 +--> Validate
 |
 +--> Detect format
 |
 +--> Parse metadata
 |
 +--> Convert samples
 |
 v
SignalRecord
```

### Requirements

-   Validate file before processing.
-   Detect unsupported formats early.
-   Avoid loading unnecessarily large recordings entirely into RAM.
-   Provide chunked/windowed processing for large files.
-   Preserve original file and metadata references.

------------------------------------------------------------------------

# 9. Stage 2 --- Preprocessing

Operations:

-   DC offset removal.
-   Amplitude normalization.
-   Optional detrending.
-   Optional filtering.
-   Optional resampling.
-   IQ imbalance diagnostics where feasible.
-   Window selection.

The preprocessing configuration must be visible to the analyst.

Example:

``` text
Preprocessing
-------------------------
DC removal       ON
Normalization    ON
Bandpass         AUTO
Resampling       OFF
Window           1.0 sec
```

------------------------------------------------------------------------

# 10. Stage 3 --- Signal Characterization

The characterization engine computes deterministic DSP features.

## Required features

### Time-domain

-   Amplitude.
-   RMS power.
-   Peak amplitude.
-   Envelope.
-   Basic statistics.

### Frequency-domain

-   FFT.
-   PSD.
-   Dominant frequency components.
-   Occupied bandwidth estimate.
-   Spectral peaks.

### Time-frequency

-   STFT.
-   Spectrogram/waterfall.
-   Signal activity over time.

### Quality metrics

-   Approximate SNR.
-   Noise floor.
-   Peak-to-noise ratio where meaningful.

### Communication features

Where signal quality permits:

-   Instantaneous phase.
-   Instantaneous frequency.
-   Frequency deviation.
-   Symbol-rate candidates.
-   Constellation representation.
-   Cyclostationary/cyclic features as an advanced feature.

------------------------------------------------------------------------

# 11. Signal Segmentation

A recording may contain multiple transmissions or periods of silence.

The system should therefore detect candidate active regions.

``` text
Recording
------------------------------------------------
silence | SIGNAL A | silence | SIGNAL B | ...
              |                  |
              v                  v
          segment A          segment B
```

### MVP method

Start with energy/power thresholding and adaptive noise-floor
estimation.

Output:

``` json
{
  "segments": [
    {
      "start": 12.42,
      "end": 18.77,
      "duration": 6.35
    }
  ]
}
```

Advanced ML-based segmentation is optional.

------------------------------------------------------------------------

# 12. Stage 4 --- Modulation Classification

## MVP supported classes

### PSK

-   BPSK
-   QPSK
-   8PSK

### FSK

-   2-FSK
-   4-FSK
-   GFSK

### QAM

-   16-QAM
-   64-QAM, if dataset quality supports it

The exact final class set should be frozen after benchmark testing.

------------------------------------------------------------------------

# 13. Hybrid Modulation Classifier

The classifier should combine signal representations rather than relying
only on raw IQ.

### Candidate features

``` text
IQ samples
Amplitude
Phase
Instantaneous frequency
FFT/PSD
Spectrogram
Constellation
Higher-order statistical features
```

### Architecture

``` text
                    IQ Recording
                         |
                  Preprocessing
                         |
          +--------------+--------------+
          |              |              |
         IQ          Spectrogram    Engineered
       window          window         features
          |              |              |
          +--------------+--------------+
                         |
                    ML Classifier
                         |
              Candidate probabilities
                         |
                         v
                 DSP verification
                         |
                         v
               Final classification
```

### Output

``` json
{
  "modulation": "QPSK",
  "confidence": 0.964,
  "alternatives": [
    {"label": "8PSK", "confidence": 0.021},
    {"label": "BPSK", "confidence": 0.009}
  ],
  "evidence": [
    "Four dominant constellation regions",
    "Approximate 90-degree phase separation",
    "ML classifier confidence 0.971",
    "DSP consistency check passed"
  ]
}
```

------------------------------------------------------------------------

# 14. ML Training Strategy

## Dataset

Create a controlled synthetic dataset using known signal parameters.

Each sample should have ground truth:

``` text
modulation
symbol_rate
sample_rate
snr
frequency_offset
phase_offset
timing_offset
fec
interleaver
```

### Channel variation

Generate signals under:

-   AWGN.
-   Different SNR levels.
-   Carrier-frequency offset.
-   Phase offset.
-   Timing offset.
-   Amplitude variation.
-   Fading where supported.
-   Different symbol rates.
-   Different pulse-shaping parameters.

### Dataset split

Use:

``` text
Train
Validation
Test
```

with parameter combinations in the test set that are not exact
duplicates of training examples.

This is necessary to test generalization.

------------------------------------------------------------------------

# 15. Modulation Model Requirements

The model must provide:

-   Predicted class.
-   Class probabilities.
-   Model version.
-   Input window size.
-   Preprocessing version.

Do not present a probability as a physical certainty.

Example:

``` text
Prediction:
QPSK

Confidence:
96.4%

Model:
modulation-v1.0

Validation:
DSP consistency PASS
```

------------------------------------------------------------------------

# 16. Stage 5 --- Synchronization

Before demodulation, perform supported synchronization steps.

Potential operations:

-   Coarse frequency-offset estimation.
-   Carrier recovery.
-   Timing recovery.
-   Phase recovery.
-   Matched filtering.
-   Symbol extraction.

The exact synchronization chain should be selected based on modulation
family.

``` text
Raw IQ
  |
Filtering
  |
Frequency correction
  |
Timing recovery
  |
Carrier/phase recovery
  |
Symbol samples
```

------------------------------------------------------------------------

# 17. Stage 6 --- Demodulation

## Required MVP support

### FSK

-   2-FSK.
-   4-FSK.
-   GFSK where supported.

### PSK

-   BPSK.
-   QPSK.
-   8PSK.

### QAM

-   16-QAM.
-   64-QAM where supported.

### Demodulator contract

``` python
demodulate(
    samples,
    modulation,
    sample_rate,
    symbol_rate,
    parameters
) -> DemodulationResult
```

Result:

``` json
{
  "modulation": "QPSK",
  "symbols_recovered": 150000,
  "bits_recovered": 300000,
  "estimated_ber": null,
  "status": "success"
}
```

------------------------------------------------------------------------

# 18. Stage 7 --- Bit Stream Generation

The demodulator must produce:

``` text
symbols
   |
   v
symbol decisions
   |
   v
bit mapping
   |
   v
raw bit stream
```

Example:

``` text
Recovered bits

010101001011010111001010...
```

The system should retain symbol-level information so that analysts can
trace the recovered bits back to the signal.

------------------------------------------------------------------------

# 19. Stage 8 --- Bit Stream Analysis

This is a required MVP feature.

## Functions

### Autocorrelation

Detect periodic patterns.

### Cross-correlation

Compare signal segments or streams.

### Repetition detection

Find repeated byte/bit sequences.

### Preamble candidate detection

Identify highly repetitive or statistically distinctive prefixes.

### Hamming-distance comparison

Measure similarity between candidate sequences.

### Visualization

``` text
Bit Stream
────────────────────────────────────

01010101 11001010 01010101 11001010
^^^^^^^^
Possible repeated sequence
```

Output:

``` json
{
  "pattern": "01010101",
  "occurrences": 27,
  "period": 64,
  "correlation_score": 0.94
}
```

------------------------------------------------------------------------

# 20. Stage 9 --- De-interleaving

## MVP

Implement and validate:

-   Block de-interleaving.

## Extended MVP / Phase 2

Implement:

-   Convolutional de-interleaving.
-   Diagonal de-interleaving.
-   Pseudo-random de-interleaving.

### Important design rule

De-interleaving should be treated as a parameterized operation.

``` text
type
depth
width
permutation parameters
seed (for pseudo-random)
```

Do not claim that the system can always infer these parameters
automatically.

------------------------------------------------------------------------

# 21. Stage 10 --- FEC

## MVP

### Convolutional codes

-   Viterbi decoding.
-   Configurable code rate where practical.
-   Configurable constraint length/polynomials for the supported demo
    cases.

### Reed-Solomon

-   Configurable supported RS parameter sets.
-   Error/erasure reporting.

## Phase 2

-   LDPC.
-   Concatenated codes.

------------------------------------------------------------------------

# 22. FEC Hypothesis Engine

Instead of pretending that FEC can always be uniquely detected:

``` text
Recovered bit stream
        |
        v
Candidate generation
        |
   +----+----+----+
   |    |    |    |
 Conv   RS   LDPC  ...
   |    |    |    |
 Decode each candidate
        |
        v
Validation metrics
        |
        v
Ranked hypotheses
```

Example:

``` text
Candidate FEC
--------------------------------
Convolutional 1/2      score 0.71
RS(255,223)            score 0.23
LDPC                   score 0.06
```

The UI should call these **hypotheses**, not ground truth.

Validation signals can include:

-   Decoder success/failure.
-   Syndrome/error metrics.
-   CRC validity if a known CRC is available.
-   Frame consistency.
-   Repetition/structure.
-   Bit entropy changes.
-   Expected code constraints.

------------------------------------------------------------------------

# 23. Recovery Validation

Every decoding attempt should have a validation layer.

``` text
Demodulation
     |
     v
Bit stream
     |
     v
De-interleave
     |
     v
FEC decode
     |
     v
Validation
     |
     +--> valid frames?
     +--> code constraints satisfied?
     +--> CRC/checksum if available?
     +--> structural consistency?
     |
     v
Recovery confidence
```

This prevents the system from reporting arbitrary decoder output as a
successful recovery.

------------------------------------------------------------------------

# 24. Confidence Model

The system should separate:

### Measurement

Directly computed:

``` text
SNR = 14.2 dB
Bandwidth = 480 kHz
```

### Estimate

Derived from signal characteristics:

``` text
Symbol rate ≈ 250 kSym/s
```

### Classification

Model-based:

``` text
QPSK confidence = 96.4%
```

### Hypothesis

Inference requiring validation:

``` text
FEC hypothesis = convolutional 1/2
confidence = 72%
```

Use these labels consistently throughout the GUI.

------------------------------------------------------------------------

# 25. Analyst GUI

The GUI should be an **analysis workstation**, not a generic SaaS
dashboard.

## Main layout

``` text
+----------------------------------------------------------+
| SIGNAL ANALYZER                     File    [ANALYZE]    |
+-------------+--------------------------------------------+
| SIGNAL INFO |                                            |
|             |                 WATERFALL                  |
| Sample Rate |                                            |
| Center Freq|--------------------------------------------|
| Duration    |                                            |
| SNR         |                CONSTELLATION               |
| Bandwidth   |                                            |
|             |--------------------------------------------|
|             |                    PSD                     |
+-------------+--------------------------------------------+
| AUTOMATED ANALYSIS                                       |
| Modulation       QPSK               96.4%                |
| Symbol Rate      ~250 kSym/s        87.2%                |
| FEC              Conv. 1/2          72.0%                |
| Interleaving     Unknown                                  |
+----------------------------------------------------------+
| RECOVERY                                                  |
| [Demodulate] [De-interleave] [FEC Decode] [Correlate]    |
+----------------------------------------------------------+
| BIT STREAM / RESULTS                                     |
+----------------------------------------------------------+
```

------------------------------------------------------------------------

# 26. Required GUI Views

## View 1 --- Upload

-   Drag-and-drop.
-   File picker.
-   Format detection.
-   Metadata summary.
-   Manual metadata entry.

## View 2 --- Signal Overview

-   Waveform.
-   PSD.
-   Waterfall.
-   Active segment selection.

## View 3 --- Automated Analysis

Display:

-   Sampling rate.
-   Bandwidth.
-   SNR.
-   Frequency information.
-   Modulation.
-   Symbol rate.
-   FEC hypothesis.
-   Interleaving hypothesis.

## View 4 --- Constellation

-   Raw constellation.
-   Corrected constellation.
-   Zoom/pan.
-   Number of clusters.
-   Optional decision boundaries.

## View 5 --- Recovery

-   Demodulation status.
-   De-interleaving configuration.
-   FEC configuration.
-   Decoder result.
-   Validation status.

## View 6 --- Bit Stream

-   Binary view.
-   Hex view.
-   Byte grouping.
-   Search.
-   Correlation.
-   Repeated-pattern highlighting.

## View 7 --- Report

Export:

-   JSON.
-   CSV where appropriate.
-   Human-readable analysis report.

------------------------------------------------------------------------

# 27. Manual Override

Every automated parameter that can materially affect recovery should be
editable.

Example:

``` text
Modulation
[ Auto ▼ ]

Symbol Rate
[ 250000 ]

Samples/Symbol
[ 9.6 ]

FEC
[ Convolutional 1/2 ▼ ]

Interleaver
[ Block ▼ ]
```

When an analyst changes a parameter:

``` text
parameter changed manually
        |
        v
re-run affected pipeline
        |
        v
new result
```

Record the override in the analysis provenance.

------------------------------------------------------------------------

# 28. Backend Architecture

## Recommended stack

### Frontend

``` text
Next.js / React
TypeScript
Tailwind CSS
WebGL-capable visualization library where required
```

### API / orchestration

``` text
Python
FastAPI
Pydantic
```

### DSP

``` text
NumPy
SciPy
GNU Radio
liquid-dsp / suitable FEC libraries
```

### ML

``` text
PyTorch
```

### Storage

MVP can use filesystem/object storage for raw recordings and JSON
metadata.

Optional:

``` text
PostgreSQL
```

for analysis history.

------------------------------------------------------------------------

# 29. Backend Module Structure

``` text
backend/
|
+-- api/
|   +-- routes/
|       +-- upload.py
|       +-- analysis.py
|       +-- demodulation.py
|       +-- recovery.py
|       +-- correlation.py
|
+-- ingestion/
|   +-- wav_reader.py
|   +-- iq_reader.py
|   +-- sigmf_reader.py
|   +-- normalizer.py
|
+-- dsp/
|   +-- preprocessing.py
|   +-- fft.py
|   +-- psd.py
|   +-- waterfall.py
|   +-- segmentation.py
|   +-- bandwidth.py
|   +-- snr.py
|   +-- synchronization.py
|   +-- symbol_rate.py
|
+-- modulation/
|   +-- classifier.py
|   +-- features.py
|   +-- models/
|   +-- verification.py
|
+-- demod/
|   +-- fsk.py
|   +-- psk.py
|   +-- qam.py
|
+-- recovery/
|   +-- bitstream.py
|   +-- interleaving/
|   +-- fec/
|       +-- viterbi.py
|       +-- reed_solomon.py
|       +-- ldpc.py
|
+-- correlation/
|   +-- autocorrelation.py
|   +-- cross_correlation.py
|   +-- pattern_detection.py
|
+-- reporting/
|   +-- report_builder.py
|   +-- provenance.py
|
+-- schemas/
+-- tests/
```

------------------------------------------------------------------------

# 30. API Design

## POST `/api/v1/files`

Upload recording.

Response:

``` json
{
  "file_id": "abc123",
  "format": "iq",
  "status": "accepted"
}
```

## POST `/api/v1/analysis`

Start analysis.

``` json
{
  "file_id": "abc123",
  "segment": {
    "start": 0,
    "end": 10
  },
  "mode": "automatic"
}
```

## GET `/api/v1/analysis/{id}`

Return current analysis status/result.

## POST `/api/v1/demodulate`

Run a selected demodulator.

## POST `/api/v1/recovery`

Run de-interleaving/FEC pipeline.

## POST `/api/v1/correlation`

Run bit-stream correlation.

## GET `/api/v1/analysis/{id}/report`

Export final report.

------------------------------------------------------------------------

# 31. Processing Job Model

Signal processing can be computationally expensive.

Do not make the browser wait on a single blocking HTTP request for large
recordings.

Use:

``` text
Frontend
   |
   v
FastAPI
   |
   v
Job Manager
   |
   v
Processing Worker
   |
   +--> DSP
   +--> ML
   +--> Demod
   +--> Recovery
   |
   v
Results Store
   |
   v
Frontend
```

For the first prototype, a lightweight in-process/background worker is
acceptable.

A queue such as Redis/Celery/RQ can be introduced if processing volume
requires it.

------------------------------------------------------------------------

# 32. Data Flow

``` text
                   +----------------+
                   |   User Upload  |
                   +-------+--------+
                           |
                           v
                   +---------------+
                   | Format Parser |
                   +-------+-------+
                           |
                           v
                   +---------------+
                   | Normalization |
                   +-------+-------+
                           |
                           v
                   +---------------+
                   | Preprocessing |
                   +-------+-------+
                           |
                           v
                   +---------------+
                   | Characterize  |
                   +-------+-------+
                           |
              +------------+------------+
              |                         |
              v                         v
      Visualization               ML Classifier
              |                         |
              +------------+------------+
                           |
                           v
                    DSP Verification
                           |
                           v
                     Demodulation
                           |
                           v
                     Bit Stream
                           |
                +----------+----------+
                |                     |
                v                     v
          Correlation            Recovery
                                      |
                              +-------+-------+
                              |               |
                              v               v
                       De-interleaving       FEC
                              |               |
                              +-------+-------+
                                      |
                                      v
                                  Validation
                                      |
                                      v
                                    Report
```

------------------------------------------------------------------------

# 33. Performance Requirements

The MVP should optimize for responsiveness rather than strict real-time
operation.

### Target

For a representative demo recording:

-   Upload/parse: \< 5 seconds.
-   Initial visualization: \< 5 seconds.
-   Automated characterization: \< 10 seconds.
-   Modulation classification: \< 5 seconds after features are
    available.
-   Demodulation: ideally faster than recording duration for
    representative short files.

These are **engineering targets**, not guarantees.

Benchmark using fixed test recordings and document hardware.

------------------------------------------------------------------------

# 34. Large File Strategy

Never assume a multi-gigabyte IQ file can be loaded directly into
browser memory.

Use:

``` text
Raw file
   |
   v
Server-side chunking
   |
   v
Selected analysis window
   |
   +--> low-resolution preview
   |
   +--> high-resolution selected region
```

For visualization:

``` text
Full signal
    |
downsample/aggregate
    |
overview plot
```

When the analyst zooms:

``` text
selected region
    |
higher-resolution samples
    |
plot
```

------------------------------------------------------------------------

# 35. Testing Strategy

## Unit tests

Test:

-   WAV parser.
-   IQ parser.
-   Metadata extraction.
-   FFT.
-   PSD.
-   bandwidth estimator.
-   SNR estimator.
-   demodulators.
-   bit mapping.
-   de-interleavers.
-   FEC decoders.
-   correlation.

## Integration tests

``` text
known IQ
  |
analysis
  |
modulation
  |
demod
  |
bits
  |
FEC
  |
expected payload
```

## ML tests

Measure:

-   Accuracy.
-   Precision.
-   Recall.
-   Confusion matrix.
-   Accuracy vs SNR.
-   Accuracy vs frequency offset.
-   Accuracy vs timing offset.

## Recovery tests

Measure:

-   BER before decoding.
-   BER after decoding.
-   Frame recovery rate.
-   Decoder failure rate.

------------------------------------------------------------------------

# 36. Ground-Truth Test Suite

Create deterministic test fixtures.

Example:

``` text
fixtures/
|
+-- bpsk/
|   +-- clean/
|   +-- snr_10/
|   +-- snr_5/
|
+-- qpsk/
|
+-- 8psk/
|
+-- 2fsk/
|
+-- gfsk/
|
+-- qam16/
|
+-- fec/
|   +-- conv_1_2/
|   +-- rs/
|
+-- interleaving/
    +-- block/
```

Every fixture must contain:

``` text
raw signal
ground-truth metadata
expected symbols
expected bits
expected decoded payload
```

------------------------------------------------------------------------

# 37. Evaluation Dashboard

For the final demo and development process, track:

``` text
MODULATION CLASSIFICATION
Accuracy
Confusion matrix
Accuracy vs SNR

DEMODULATION
Symbol recovery rate
BER

FEC
Pre-FEC BER
Post-FEC BER
Frame recovery rate

SEGMENTATION
Precision
Recall

SYSTEM
Processing time
Memory usage
File size
```

This turns the project from a visual prototype into an evaluated
engineering system.

------------------------------------------------------------------------

# 38. Security and Data Handling

Because the intended organization is NTRO and recordings may be
sensitive:

-   Do not send uploaded signal recordings to external AI APIs.
-   Keep processing local/server-controlled.
-   Do not log raw signal contents unnecessarily.
-   Avoid storing uploaded recordings permanently unless required.
-   Separate raw data from derived results.
-   Record access and processing provenance in production-oriented
    versions.
-   Use authentication if deployed beyond a local demo.

The MVP should be designed so that ML inference is local.

------------------------------------------------------------------------

# 39. AI/ML Boundary

## ML should handle

-   Modulation classification.
-   Optional signal segmentation.
-   Optional feature-based signal family classification.
-   Candidate ranking where sufficient labelled data exists.

## Classical DSP should handle

-   FFT.
-   PSD.
-   Filtering.
-   Synchronization.
-   Frequency estimation.
-   Symbol timing.
-   Demodulation.
-   Correlation.
-   Known FEC decoding.

## Hypothesis engine should handle

-   Candidate FEC configurations.
-   Candidate interleaver configurations.
-   Validation and ranking.

This division is a core architectural principle.

------------------------------------------------------------------------

# 40. Recommended MVP Feature Matrix

  Feature                                          MVP       Phase 2
  --------------------------------- ------------------ -------------
  WAV ingestion                                    YES 
  Raw IQ ingestion                                 YES 
  SigMF                                            YES 
  Metadata handling                                YES 
  Waveform                                         YES 
  FFT/PSD                                          YES 
  Waterfall                                        YES 
  Constellation                                    YES 
  SNR                                              YES 
  Bandwidth                                        YES 
  Signal segmentation                              YES   Advanced ML
  BPSK                                             YES 
  QPSK                                             YES 
  8PSK                                             YES 
  2FSK                                             YES 
  4FSK                                             YES 
  GFSK                                             YES 
  16QAM                                            YES 
  64QAM                                       Optional           YES
  Demodulation                                     YES 
  Bit-stream extraction                            YES 
  Correlation                                      YES 
  Preamble/pattern detection                       YES 
  Block de-interleaving                            YES 
  Viterbi                                          YES 
  Reed-Solomon                                     YES 
  Convolutional interleaving                                     YES
  Diagonal interleaving                                          YES
  Pseudo-random interleaving                                     YES
  LDPC                                                           YES
  Concatenated FEC                                               YES
  Automatic FEC detection             Hypothesis-based      Advanced
  Automatic interleaver detection     Hypothesis-based      Advanced
  Protocol identification                                     Future
  Live SDR                                                    Future

------------------------------------------------------------------------

# 41. "Must Have" vs "Should Have" vs "Do Not Build"

## Must Have

1.  WAV/IQ ingestion.
2.  Metadata normalization.
3.  Waveform.
4.  PSD.
5.  Waterfall.
6.  Constellation.
7.  Signal characterization.
8.  Modulation classification.
9.  FSK/PSK/QAM demodulation.
10. Bit-stream extraction.
11. Correlation.
12. At least one de-interleaver.
13. Viterbi.
14. Reed-Solomon.
15. Confidence/evidence.
16. Manual override.
17. Exportable report.
18. Quantitative benchmark results.

## Should Have

1.  SigMF.
2.  Signal segmentation.
3.  GFSK.
4.  64-QAM.
5.  Additional interleavers.
6.  LDPC.
7.  FEC hypothesis ranking.
8.  Processing provenance.
9.  Large-file windowing.
10. Analysis history.

## Do Not Build for MVP

1.  Universal protocol decoder.
2.  Universal FEC classifier.
3.  Universal interleaver classifier.
4.  Live SDR ingestion.
5.  Real-time multi-sensor processing.
6.  Full RF spectrum monitoring.
7.  Payload semantic interpretation.
8.  Cryptographic decryption.
9.  Giant end-to-end neural network.

------------------------------------------------------------------------

# 42. Demonstration Scenario

The final SIH demonstration should use a **known ground-truth signal**
whose parameters are hidden from the UI initially.

Example:

``` text
Input:
unknown_signal.iq
```

### Step 1

System identifies:

``` text
Format: IQ
Sample rate: 2.4 MS/s
Duration: 10 sec
```

### Step 2

Show:

``` text
Waveform
Waterfall
PSD
```

### Step 3

Automatic analysis:

``` text
Modulation: QPSK
Confidence: 96%
Symbol rate: ~250 kSym/s
SNR: ~14 dB
```

### Step 4

System demodulates:

``` text
IQ
 ↓
symbols
 ↓
bits
```

### Step 5

Bit analysis finds:

``` text
Repeated sequence
Potential preamble
```

### Step 6

Recovery:

``` text
Candidate:
Convolutional 1/2
```

Run decoder.

### Step 7

Validation:

``` text
Pre-FEC BER: 7.8%
Post-FEC BER: 0.02%
Frame validation: PASS
```

### Step 8

Show final report:

``` text
Signal characterization
        +
Modulation
        +
Recovery chain
        +
Bit-stream evidence
        +
Confidence
        +
Processing provenance
```

This gives judges a complete story from **raw recording to recovered
information**.

------------------------------------------------------------------------

# 43. Failure Demo

A second scenario should demonstrate uncertainty.

Input:

``` text
low_snr_unknown.iq
```

System reports:

``` text
Modulation:
QPSK — 61%

FEC:
No reliable hypothesis

Interleaving:
Unknown

Recovery:
Incomplete
```

Then:

``` text
Reasons:
- low SNR
- unstable timing estimate
- insufficient samples
- no validated FEC hypothesis
```

This is important because a credible analysis system must know when it
does not have enough evidence.

------------------------------------------------------------------------

# 44. Suggested Team Architecture

For a 5-person team:

### Person 1 --- DSP / Signal Processing

Own:

-   IQ/WAV.
-   preprocessing.
-   FFT.
-   PSD.
-   waterfall.
-   SNR.
-   bandwidth.
-   synchronization.

### Person 2 --- ML / Signal Classification

Own:

-   dataset generation.
-   feature extraction.
-   modulation classifier.
-   model evaluation.
-   confidence system.

### Person 3 --- Demodulation / Recovery

Own:

-   FSK/PSK/QAM demodulation.
-   bit recovery.
-   Viterbi.
-   Reed-Solomon.
-   interleaving.

### Person 4 --- Backend / Integration

Own:

-   FastAPI.
-   processing jobs.
-   pipeline orchestration.
-   APIs.
-   result schemas.
-   provenance.

### Person 5 --- Frontend / Visualization

Own:

-   GUI.
-   waveform.
-   waterfall.
-   constellation.
-   analysis dashboard.
-   bit-stream viewer.
-   report UI.

Everyone should understand the full pipeline even if ownership is
divided.

------------------------------------------------------------------------

# 45. Development Phases

## Phase 0 --- Technical Spike

**Goal:** Prove the core DSP pipeline.

Deliver:

``` text
IQ
 ↓
FFT
 ↓
PSD
 ↓
waterfall
 ↓
constellation
```

No fancy GUI.

------------------------------------------------------------------------

## Phase 1 --- Ingestion + Visualization

Deliver:

-   WAV.
-   IQ.
-   metadata.
-   waveform.
-   PSD.
-   waterfall.
-   constellation.

------------------------------------------------------------------------

## Phase 2 --- Automated Characterization

Deliver:

-   SNR.
-   bandwidth.
-   signal segmentation.
-   frequency features.
-   symbol-rate estimation.

------------------------------------------------------------------------

## Phase 3 --- Modulation Classification

Deliver:

-   dataset.
-   classifier.
-   evaluation.
-   confidence.
-   DSP verification.

------------------------------------------------------------------------

## Phase 4 --- Demodulation

Deliver:

-   BPSK.
-   QPSK.
-   8PSK.
-   2FSK/4FSK.
-   16QAM.
-   bit recovery.

------------------------------------------------------------------------

## Phase 5 --- Recovery

Deliver:

-   block de-interleaving.
-   Viterbi.
-   Reed-Solomon.
-   validation.

------------------------------------------------------------------------

## Phase 6 --- Correlation

Deliver:

-   autocorrelation.
-   cross-correlation.
-   repeated pattern detection.
-   preamble candidates.

------------------------------------------------------------------------

## Phase 7 --- Analyst GUI

Integrate the complete pipeline.

------------------------------------------------------------------------

## Phase 8 --- Benchmarking

Run fixed datasets.

Produce:

-   accuracy.
-   BER.
-   recovery rate.
-   latency.
-   failure cases.

------------------------------------------------------------------------

## Phase 9 --- Advanced Features

Only after MVP is stable:

-   LDPC.
-   additional interleavers.
-   FEC hypothesis engine.
-   advanced segmentation.
-   64-QAM.
-   additional modulation families.

------------------------------------------------------------------------

# 46. Definition of Done

The MVP is considered complete only when a clean test recording can pass
through:

``` text
UPLOAD
  ↓
PARSE
  ↓
VISUALIZE
  ↓
CHARACTERIZE
  ↓
CLASSIFY
  ↓
DEMODULATE
  ↓
BIT STREAM
  ↓
CORRELATE
  ↓
DE-INTERLEAVE
  ↓
FEC
  ↓
VALIDATE
  ↓
REPORT
```

and each stage produces a testable output.

The project should also have at least one end-to-end test where the
original transmitted payload is known and the system demonstrates
measurable recovery.

------------------------------------------------------------------------

# 47. Core Engineering Principle

The system should follow:

> **Observe → Measure → Hypothesize → Process → Validate → Report**

rather than:

> **Upload → AI → Answer**

This principle should guide both the architecture and the SIH
presentation.

------------------------------------------------------------------------

# 48. Final MVP Definition

### The MVP is:

> A local/server-hosted GUI application that accepts WAV/IQ/SigMF
> recordings, extracts and visualizes signal characteristics,
> automatically classifies a defined set of digital modulations using a
> hybrid DSP + ML pipeline, demodulates supported signals into bit
> streams, performs correlation and pattern analysis, and applies
> selected de-interleaving/FEC recovery with evidence-backed confidence
> and validation.

### The MVP is not:

> A universal automated communications-intelligence system capable of
> identifying and decoding arbitrary unknown signals.

The distinction is deliberate. The first is an achievable engineering
product; the second is an open-ended research problem.

------------------------------------------------------------------------

# 49. Success Criteria

The project should be considered successful if it demonstrates:

### Signal analysis

-   Correct parsing of supported recordings.
-   Accurate visualization.
-   Reliable measurable signal features.

### ML

-   Strong modulation classification on held-out test data.
-   Published confusion matrix.
-   Performance characterization across SNR.

### DSP

-   Successful demodulation of supported modulations.
-   Reproducible symbol/bit recovery.

### Recovery

-   Demonstrable improvement after FEC on ground-truth signals.
-   Correct operation of selected de-interleaving methods.

### Correlation

-   Detection of known/repeated patterns in test bit streams.

### System

-   End-to-end pipeline execution.
-   Clear confidence/evidence.
-   Manual parameter override.
-   Exportable results.
-   Reproducible test suite.

------------------------------------------------------------------------

# 50. Open Technical Questions to Resolve Before Full Implementation

These should be answered experimentally during Phase 0:

1.  What exact IQ encodings will the SIH evaluation recordings use?
2.  Will evaluation recordings include SigMF or equivalent metadata?
3.  Which modulation families will be represented in the available test
    data?
4.  What SNR range should the classifier support?
5.  Which symbol rates need to be supported?
6.  Which FEC parameter configurations should be demonstrated?
7.  What interleaver parameter ranges are expected?
8.  What is the maximum expected recording size?
9.  Is center-frequency metadata always available?
10. What constitutes successful bit-stream correlation for evaluation?
11. Which payload/frame validation information is available?
12. Which parts of the system need to operate completely offline?

These questions should be answered from organizer-provided sample data
if available rather than assumed.

------------------------------------------------------------------------

# 51. Recommended First Technical Experiment

Before building the full system, create one controlled signal:

``` text
Known payload
    ↓
QPSK
    ↓
Convolutional FEC
    ↓
Block interleaver
    ↓
Channel noise
    ↓
IQ recording
```

Then build:

``` text
IQ
 ↓
QPSK detection
 ↓
QPSK demodulation
 ↓
de-interleaving
 ↓
Viterbi
 ↓
original payload
```

If the team can make this pipeline work reliably, the architecture is
validated.

Only then expand to:

``` text
BPSK
8PSK
FSK
QAM
RS
LDPC
additional interleavers
```

------------------------------------------------------------------------

# 52. Final Architectural Summary

``` text
                         ┌───────────────────────┐
                         │      ANALYST GUI      │
                         │                       │
                         │ Upload / Visualize    │
                         │ Analyze / Recover     │
                         │ Inspect / Override    │
                         └───────────┬───────────┘
                                     │
                                  REST/WS
                                     │
                         ┌───────────▼───────────┐
                         │      FASTAPI API      │
                         │    Pipeline Manager   │
                         └───────────┬───────────┘
                                     │
                   ┌─────────────────┼─────────────────┐
                   │                 │                 │
                   ▼                 ▼                 ▼
             INGESTION             DSP               ML
                   │                 │                 │
             WAV / IQ /        FFT / PSD /       Modulation
                SigMF          Waterfall /       classifier
                   │            SNR / BW              │
                   │                 │                 │
                   └─────────────────┼─────────────────┘
                                     │
                                     ▼
                           SIGNAL HYPOTHESIS
                                     │
                                     ▼
                              SYNCHRONIZATION
                                     │
                                     ▼
                              DEMODULATION
                          FSK / PSK / QAM
                                     │
                                     ▼
                               BIT STREAM
                                     │
                         ┌───────────┴───────────┐
                         ▼                       ▼
                   CORRELATION               RECOVERY
                         │                 ┌─────┴─────┐
                         │                 ▼           ▼
                         │          DE-INTERLEAVE     FEC
                         │                 │           │
                         │                 └─────┬─────┘
                         │                       ▼
                         │                  VALIDATION
                         │                       │
                         └───────────────────────┤
                                                 ▼
                                         EVIDENCE REPORT
```

------------------------------------------------------------------------

## 53. One-Sentence Product Definition

**SIH26147 MVP = an evidence-driven RF signal analysis workstation that
turns `.IQ`/`.WAV` recordings into visual signal intelligence,
modulation hypotheses, recovered bit streams, and validated decoding
results through a hybrid DSP + ML + configurable recovery pipeline.**
