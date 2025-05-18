from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from twiml_response import build_twiml_response, build_recording_response
import requests

app = FastAPI()

@app.post("/voice")
async def voice_response(request: Request):
    twiml = build_twiml_response()
    return Response(content=twiml, media_type="application/xml")

@app.post("/handle-recording")
async def handle_recording(RecordingUrl: str = Form(...), From: str = Form(...)):
    print(f"📥 Received recording from {From}: {RecordingUrl}")

    # Download the audio file
    audio_response = requests.get(RecordingUrl + ".mp3")
    audio_filename = f"recording_from_{From.replace('+', '')}.mp3"
    with open(f"/mnt/data/{audio_filename}", "wb") as f:
        f.write(audio_response.content)

    print(f"✅ Audio saved as {audio_filename}")
    return Response(content=build_recording_response(), media_type="application/xml")