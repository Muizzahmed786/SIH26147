import time
import os
import numpy as np
import sys

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.ingestion.iq_reader import read_iq
from app.ingestion.normalizer import normalize_signal
from app.dsp.pipeline import compute_fft, compute_psd, compute_waterfall, extract_constellation

def profile_pipeline():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures/qpsk'))
    iq_path = os.path.join(base_dir, 'signal.iq')
    params = {"sample_rate": 1000000, "dtype": "complex64"}
    
    times = {}
    
    t0 = time.time()
    record, signal = read_iq(iq_path, params)
    times['iq_read'] = time.time() - t0
    
    t0 = time.time()
    norm_sig = normalize_signal(signal)
    times['normalization'] = time.time() - t0
    
    t0 = time.time()
    fft_res = compute_fft(norm_sig, record.sample_rate)
    times['fft'] = time.time() - t0
    
    t0 = time.time()
    psd_res = compute_psd(norm_sig, record.sample_rate)
    times['psd'] = time.time() - t0
    
    t0 = time.time()
    wf_res = compute_waterfall(norm_sig, record.sample_rate)
    times['waterfall'] = time.time() - t0
    
    t0 = time.time()
    const_res = extract_constellation(norm_sig)
    times['constellation'] = time.time() - t0
    
    print("Profiling Results:")
    for k, v in times.items():
        print(f"{k}: {v:.4f}s")
        
if __name__ == "__main__":
    profile_pipeline()
