import numpy as np
from scipy import signal as scipy_signal
from typing import Dict, Any

def compute_fft(signal_data: np.ndarray, sample_rate: float, nfft: int = 2048) -> Dict[str, Any]:
    """Compute FFT for visualization."""
    # Ensure signal isn't too large for basic FFT vis, take a slice if needed
    if len(signal_data) > nfft:
        data = signal_data[:nfft]
    else:
        data = signal_data
        
    window = np.hanning(len(data))
    fft_result = np.fft.fftshift(np.fft.fft(data * window, n=nfft))
    freqs = np.fft.fftshift(np.fft.fftfreq(nfft, d=1/sample_rate))
    
    # Convert to dB
    mag = np.abs(fft_result)
    mag_db = 20 * np.log10(mag + 1e-12)
    
    return {
        "freqs": freqs.tolist(),
        "magnitudes_db": mag_db.tolist()
    }

def compute_psd(signal_data: np.ndarray, sample_rate: float, nfft: int = 1024) -> Dict[str, Any]:
    """Compute Power Spectral Density."""
    freqs, psd = scipy_signal.welch(signal_data, fs=sample_rate, nperseg=nfft, return_onesided=False)
    
    # Shift so 0 Hz is in the middle for complex signals
    freqs = np.fft.fftshift(freqs)
    psd = np.fft.fftshift(psd)
    psd_db = 10 * np.log10(psd + 1e-12)
    
    return {
        "freqs": freqs.tolist(),
        "psd_db": psd_db.tolist()
    }

def compute_waterfall(signal_data: np.ndarray, sample_rate: float, nperseg: int = 256, noverlap: int = 128) -> Dict[str, Any]:
    """Compute spectrogram for waterfall plot."""
    # Limit data for waterfall to avoid huge payloads
    max_samples = 100000
    if len(signal_data) > max_samples:
        signal_data = signal_data[:max_samples]
        
    freqs, times, Sxx = scipy_signal.spectrogram(signal_data, fs=sample_rate, nperseg=nperseg, noverlap=noverlap, return_onesided=False, mode='complex')
    
    freqs = np.fft.fftshift(freqs)
    Sxx = np.fft.fftshift(Sxx, axes=0)
    Sxx_db = 10 * np.log10(np.abs(Sxx)**2 + 1e-12)
    
    return {
        "freqs": freqs.tolist(),
        "times": times.tolist(),
        "spectrogram_db": Sxx_db.tolist()
    }

def extract_constellation(signal_data: np.ndarray, num_points: int = 2000) -> Dict[str, Any]:
    """
    Extract raw I/Q points for a basic constellation plot.
    Since we don't have symbol sync yet, this is just a scatter of raw complex points.
    """
    if len(signal_data) > num_points:
        points = signal_data[:num_points]
    else:
        points = signal_data
        
    return {
        "i": np.real(points).tolist(),
        "q": np.imag(points).tolist()
    }
