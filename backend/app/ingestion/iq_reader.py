import numpy as np
import uuid
import os
from typing import Dict, Any
from app.schemas.signal import SignalRecord

def read_iq(file_path: str, params: Dict[str, Any]) -> tuple[SignalRecord, np.ndarray]:
    """
    Read raw IQ file. Requires metadata explicitly passed in params.
    Expected params:
    - sample_rate (float)
    - dtype (e.g., 'complex64', 'float32', 'int16')
    """
    sample_rate = params.get('sample_rate')
    dtype_str = params.get('dtype', 'complex64')
    
    if sample_rate is None:
        raise ValueError("Sample rate is required for raw IQ files.")
        
    dtype_map = {
        'complex64': np.complex64,
        'float32': np.float32,
        'int16': np.int16,
        'uint8': np.uint8
    }
    
    if dtype_str not in dtype_map:
        raise ValueError(f"Unsupported dtype: {dtype_str}")
        
    dt = dtype_map[dtype_str]
    data = np.fromfile(file_path, dtype=dt)
    
    # If float32 or int16, we assume interleaved I and Q
    if dtype_str != 'complex64':
        if len(data) % 2 != 0:
            data = data[:-1]
        i = data[0::2].astype(np.float32)
        q = data[1::2].astype(np.float32)
        signal_data = i + 1j * q
    else:
        signal_data = data.astype(np.complex64)
        
    sample_count = len(signal_data)
    duration = sample_count / sample_rate
    
    record = SignalRecord(
        id=str(uuid.uuid4()),
        source_file=os.path.basename(file_path),
        source_format="iq",
        sample_rate=sample_rate,
        channels=2, # I and Q
        sample_count=sample_count,
        duration=duration,
        dtype=dtype_str,
        metadata=params,
        metadata_source="user_input",
        analysis_status="ingested"
    )
    
    return record, signal_data
