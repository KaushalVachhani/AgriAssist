"""
FastAPI app for Farm AI Assistant | खेत सहायक AI
Serves API endpoints and static frontend files.
"""

import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from agriassist.handlers import validate_and_handle
from agriassist.config import load_env_and_models

# Load model once at startup
model = load_env_and_models()

app = FastAPI(title="Farm AI Assistant | खेत सहायक AI")

# CORS for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory for generated audio responses
AUDIO_DIR = Path(__file__).parent / "generated_speech_responses"
AUDIO_DIR.mkdir(exist_ok=True)

@app.post("/api/query")
async def query(
    text: str = Form(None),
    image: UploadFile = File(None),
    audio: UploadFile = File(None)
):
    image_path = None
    audio_path = None
    if image and image.filename:
        image_path = f"/tmp/{image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    if audio and audio.filename:
        audio_path = f"/tmp/{audio.filename}"
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
    text_response, audio_response = validate_and_handle(text, image_path, audio_path, model=model)
    audio_url = None
    if audio_response:
        audio_filename = Path(audio_response).name
        audio_url = f"/audio/{audio_filename}"
    result = {"text": text_response, "audio": audio_url}
    return JSONResponse(result)

# Mount static frontend and audio files
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
