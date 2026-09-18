import pytest
import os
import numpy as np
from app.ingestion.wav_reader import read_wav
from app.ingestion.iq_reader import read_iq
from app.ingestion.normalizer import normalize_signal
from app.dsp.pipeline import compute_fft, compute_psd, compute_waterfall, extract_constellation

def test_qpsk_pipeline():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../fixtures/qpsk'))
    wav_path = os.path.join(base_dir, 'signal.wav')
    iq_path = os.path.join(base_dir, 'signal.iq')
    
    assert os.path.exists(wav_path), "WAV fixture not generated"
    assert os.path.exists(iq_path), "IQ fixture not generated"
    
    # Test IQ reading
    params = {"sample_rate": 1000000, "dtype": "complex64"}
    record, signal = read_iq(iq_path, params)
    
    assert record.sample_rate == 1000000
    assert record.channels == 2
    assert len(signal) > 0
    assert np.iscomplexobj(signal)
    
    # Test Normalization
    norm_sig = normalize_signal(signal)
    assert np.max(np.abs(norm_sig)) <= 1.0 + 1e-6
    
    # Test FFT
    fft_res = compute_fft(norm_sig, record.sample_rate)
    assert "freqs" in fft_res
    assert "magnitudes_db" in fft_res
    assert len(fft_res["freqs"]) == len(fft_res["magnitudes_db"])
    
    # Test Constellation
    const = extract_constellation(norm_sig)
    assert "i" in const
    assert "q" in const
    assert len(const["i"]) == len(const["q"])
