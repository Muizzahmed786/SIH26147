import numpy as np
import json
import os
import uuid
from typing import Tuple
from app.schemas.signal import SignalRecord

def read_sigmf(meta_path: str) -> Tuple[SignalRecord, np.ndarray]:
    """
    Basic SigMF reader. Expects .sigmf-meta file path.
    Assumes .sigmf-data is in the same directory.
    """
    with open(meta_path, 'r') as f:
        meta = json.load(f)
        
    global_meta = meta.get('global', {})
    captures_meta = meta.get('captures', [{}])[0]
    
    sample_rate = global_meta.get('core:sample_rate', 1.0)
    dtype_str = global_meta.get('core:datatype', 'cf32_le')
    
    # Map SigMF datatypes to numpy
    # cf32_le -> complex float 32 little endian (np.complex64)
    # ci16_le -> complex int 16 little endian (np.int16 interleaved)
    dt = np.complex64
    if dtype_str == 'ci16_le':
        dt = np.int16
    elif dtype_str == 'cf32_le':
        dt = np.complex64
    
    data_path = meta_path.replace('.sigmf-meta', '.sigmf-data')
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Missing data file: {data_path}")
        
    data = np.fromfile(data_path, dtype=dt)
    
    if dtype_str == 'ci16_le':
        if len(data) % 2 != 0:
            data = data[:-1]
        signal_data = data[0::2].astype(np.float32) + 1j * data[1::2].astype(np.float32)
    else:
        signal_data = data
        
    sample_count = len(signal_data)
    duration = sample_count / sample_rate
    
    record = SignalRecord(
        id=str(uuid.uuid4()),
        source_file=os.path.basename(meta_path),
        source_format="sigmf",
        sample_rate=sample_rate,
        channels=2,
        sample_count=sample_count,
        duration=duration,
        dtype=dtype_str,
        metadata=meta,
        metadata_source="metadata",
        analysis_status="ingested"
    )
    
    return record, signal_data
