from pydantic import BaseModel
from typing import Dict, Any, Optional

class SignalRecord(BaseModel):
    id: str
    source_file: str
    source_format: str
    
    sample_rate: float
    center_frequency: Optional[float] = None
    bandwidth: Optional[float] = None
    
    channels: int
    sample_count: int
    duration: float
    dtype: str
    
    metadata: Dict[str, Any]
    metadata_source: str # e.g., 'metadata', 'user_input', 'estimated'
    
    analysis_status: str
