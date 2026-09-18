import os
import json
import numpy as np
import scipy.io.wavfile as wavfile

def generate_qpsk(num_symbols=1000, samples_per_symbol=8, snr_db=20):
    np.random.seed(42)
    # Generate random symbols (0, 1, 2, 3)
    symbols = np.random.randint(0, 4, num_symbols)
    
    # Map to QPSK constellation (pi/4, 3pi/4, -3pi/4, -pi/4)
    phases = symbols * np.pi/2 + np.pi/4
    constellation_points = np.exp(1j * phases)
    
    # Pulse shaping (rectangular for simplicity, or raised cosine)
    # Let's use simple rectangular for now
    signal = np.repeat(constellation_points, samples_per_symbol)
    
    # Add AWGN
    # SNR = 10 * log10(P_signal / P_noise)
    # P_signal is approx 1
    p_signal = np.var(signal)
    snr_linear = 10**(snr_db / 10.0)
    p_noise = p_signal / snr_linear
    noise = np.sqrt(p_noise/2) * (np.random.randn(len(signal)) + 1j * np.random.randn(len(signal)))
    
    signal_noisy = signal + noise
    
    return signal_noisy, symbols

def main():
    base_dir = r"c:\Users\mulla\Desktop\Projects\SIH26147\fixtures\qpsk"
    os.makedirs(base_dir, exist_ok=True)
    
    sample_rate = 1_000_000 # 1 MHz
    samples_per_symbol = 8
    symbol_rate = sample_rate / samples_per_symbol # 125 kBd
    num_symbols = 4096
    snr_db = 15
    
    signal, _ = generate_qpsk(num_symbols=num_symbols, samples_per_symbol=samples_per_symbol, snr_db=snr_db)
    
    # Save as complex64 IQ
    iq_path = os.path.join(base_dir, "signal.iq")
    signal.astype(np.complex64).tofile(iq_path)
    
    # Save as WAV (converting complex to stereo float32)
    wav_path = os.path.join(base_dir, "signal.wav")
    wav_data = np.zeros((len(signal), 2), dtype=np.float32)
    wav_data[:, 0] = np.real(signal)
    wav_data[:, 1] = np.imag(signal)
    wavfile.write(wav_path, sample_rate, wav_data)
    
    # Save metadata
    metadata = {
        "sample_rate": sample_rate,
        "format": "complex64",
        "i_first": True,
        "byte_order": "little",
        "description": "Synthetic QPSK signal with AWGN"
    }
    with open(os.path.join(base_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)
        
    # Save ground truth
    ground_truth = {
        "modulation": "QPSK",
        "sample_rate": sample_rate,
        "symbol_rate": symbol_rate,
        "snr_db": snr_db,
        "number_of_symbols": num_symbols
    }
    with open(os.path.join(base_dir, "ground_truth.json"), "w") as f:
        json.dump(ground_truth, f, indent=4)

if __name__ == "__main__":
    main()
