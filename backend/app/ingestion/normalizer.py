import numpy as np

def normalize_signal(signal: np.ndarray) -> np.ndarray:
    """
    Normalize signal to have max amplitude of 1.0 (or similar reasonable scaling).
    Removes DC offset.
    """
    # Remove DC offset
    signal = signal - np.mean(signal)
    
    # Normalize amplitude
    max_amp = np.max(np.abs(signal))
    if max_amp > 0:
        signal = signal / max_amp
        
    return signal
