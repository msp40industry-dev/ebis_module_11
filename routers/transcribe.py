import numpy as np
import json
import soundfile as sf
from vosk import Model, KaldiRecognizer
from pydantic import BaseModel
from fastapi import APIRouter


MODEL_DIR = "models/vosk-model-small-es-0.42"
model = Model(MODEL_DIR)

transcribe_router = APIRouter()


class TranscribeRequest(BaseModel):
    recording_path: str


class TranscribeResponse(BaseModel):
    text: str


def load_wav_bytes_mono_int16(path):
    data, sr = sf.read(str(path), always_2d=True)
    mono = data.mean(axis=1)
    mono = np.clip(mono, -1.0, 1.0)
    return (mono * 32767).astype(np.int16).tobytes(), sr


def transcribe_wav(path, model):
    pcm, sr = load_wav_bytes_mono_int16(path)
    rec = KaldiRecognizer(model, sr)

    step = int(sr * 0.25) * 2
    for i in range(0, len(pcm), step):
        rec.AcceptWaveform(pcm[i:i+step])
    return json.loads(rec.FinalResult()).get("text", "").strip()


@transcribe_router.post("/transcribe")
async def chat_from_audio(request: TranscribeRequest):
    file_path = request.recording_path
    text = transcribe_wav(file_path, model)
    return TranscribeResponse(text=text)
