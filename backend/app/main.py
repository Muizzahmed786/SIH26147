from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import upload, analysis

app = FastAPI(title="SIH26147 DSP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev only, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(analysis.router)

@app.get("/")
def root():
    return {"status": "ok", "service": "SIH26147 DSP API"}
