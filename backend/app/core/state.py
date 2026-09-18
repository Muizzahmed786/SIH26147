from typing import Dict, Any
from app.schemas.signal import SignalRecord
import numpy as np

# In-memory storage for MVP
# In a real app this would be a DB + file storage or blob storage

class AppState:
    def __init__(self):
        self.records: Dict[str, SignalRecord] = {}
        self.signals: Dict[str, np.ndarray] = {}
        self.analyses: Dict[str, Dict[str, Any]] = {}

state = AppState()
