from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.core.state import state
from app.ingestion.normalizer import normalize_signal
from app.dsp.pipeline import compute_fft, compute_psd, compute_waterfall, extract_constellation
from pydantic import BaseModel

router = APIRouter()

class AnalysisRequest(BaseModel):
    record_id: str

def run_analysis_pipeline(record_id: str):
    if record_id not in state.signals:
        return
        
    signal_data = state.signals[record_id]
    record = state.records[record_id]
    
    # 1. Normalization
    signal_data = normalize_signal(signal_data)
    
    # 2. Extract visualization features
    sample_rate = record.sample_rate
    
    # Simple waveform slice (first 1000 samples)
    if len(signal_data) > 1000:
        waveform = signal_data[:1000]
    else:
        waveform = signal_data
        
    results = {
        "waveform": {
            "i": np.real(waveform).tolist(),
            "q": np.imag(waveform).tolist() if np.iscomplexobj(waveform) else None
        },
        "spectrum": compute_fft(signal_data, sample_rate),
        "psd": compute_psd(signal_data, sample_rate),
        "waterfall": compute_waterfall(signal_data, sample_rate),
        "constellation": extract_constellation(signal_data)
    }
    
    state.analyses[record_id] = results
    record.analysis_status = "completed"

import numpy as np # needed for the pipeline func

@router.post("/api/v1/analysis")
async def start_analysis(req: AnalysisRequest, background_tasks: BackgroundTasks):
    if req.record_id not in state.records:
        raise HTTPException(status_code=404, detail="Record not found")
        
    state.records[req.record_id].analysis_status = "processing"
    
    # For MVP we run this synchronously or very simply in background
    # Since we are returning immediately, we use background task
    background_tasks.add_task(run_analysis_pipeline, req.record_id)
    
    return {"status": "processing", "record_id": req.record_id}

@router.get("/api/v1/analysis/{record_id}")
async def get_analysis(record_id: str):
    if record_id not in state.records:
        raise HTTPException(status_code=404, detail="Record not found")
        
    record = state.records[record_id]
    
    if record.analysis_status == "completed":
        return {
            "status": "completed",
            "record": record,
            "results": state.analyses.get(record_id, {})
        }
    else:
        return {
            "status": record.analysis_status,
            "record": record
        }
