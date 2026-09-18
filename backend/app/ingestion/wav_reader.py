import scipy.io.wavfile as wavfile
import numpy as np
import uuid
import os
from app.schemas.signal import SignalRecord

def read_wav(file_path: str) -> tuple[SignalRecord, np.ndarray]:
    sample_rate, data = wavfile.read(file_path)
    
    # Handle stereo/mono
    if len(data.shape) == 1:
        channels = 1
        sample_count = len(data)
    else:
        channels = data.shape[1]
        sample_count = data.shape[0]
        
    duration = sample_count / sample_rate
    
    # If 2 channels, treat as I and Q for our purposes if needed, but for now just standard
    # Convert to complex if it's stereo? For this project, a 2-channel WAV is often I/Q.
    if channels == 2:
        # Assuming I is channel 0, Q is channel 1
        signal_data = data[:, 0].astype(np.float32) + 1j * data[:, 1].astype(np.float32)
    else:
        signal_data = data.astype(np.float32)
        
    record = SignalRecord(
        id=str(uuid.uuid4()),
        source_file=os.path.basename(file_path),
        source_format="wav",
        sample_rate=sample_rate,
        channels=channels,
        sample_count=sample_count,
        duration=duration,
        dtype=str(data.dtype),
        metadata={},
        metadata_source="metadata",
        analysis_status="ingested"
    )
    
    return record, signal_data
