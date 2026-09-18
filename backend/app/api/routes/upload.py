from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from app.core.state import state
from app.ingestion.wav_reader import read_wav
from app.ingestion.iq_reader import read_iq
import tempfile
import os
import json

router = APIRouter()

@router.post("/api/v1/files")
async def upload_file(
    file: UploadFile = File(...),
    metadata: str = Form(None)
):
    try:
        ext = os.path.splitext(file.filename)[1].lower()
        
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
            
        params = {}
        if metadata:
            try:
                params = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in metadata")
                
        if ext == ".wav":
            record, signal_data = read_wav(tmp_path)
        elif ext in [".iq", ".bin", ".dat", ".raw"]:
            record, signal_data = read_iq(tmp_path, params)
        else:
            os.unlink(tmp_path)
            raise HTTPException(status_code=400, detail=f"Unsupported file extension {ext}")
            
        os.unlink(tmp_path) # Cleanup temp file
        
        state.records[record.id] = record
        state.signals[record.id] = signal_data
        
        return {"status": "success", "record": record}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
