from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from twiml_response import build_twiml_response, build_recording_response
import requests

app = FastAPI()

# Endpoint POST per Twilio (core)
@app.post("/voice")
async def voice_response(request: Request):
    twiml = build_twiml_response()
    return Response(content=twiml, media_type="application/xml")

# Endpoint GET solo per test da browser
@app.get("/voice")
def test_voice_get():
    return Response(content="""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="it-IT">Ciao, la segreteria vocale è attiva. Prova a chiamare questo numero da un altro telefono!</Say>
</Response>""", media_type="application/xml")

# Endpoint per ricevere l'audio registrato
@app.post("/handle-recording")
async def handle_recording(RecordingUrl: str = Form(...), From: str = Form(...)):
    print(f"📥 Received recording from {From}: {RecordingUrl}")
    
    # Scarica il file audio
    audio_response = requests.get(RecordingUrl + ".mp3")
    audio_filename = f"recording_from_{From.replace('+', '')}.mp3"
    with open(f"/mnt/data/{audio_filename}", "wb") as f:
        f.write(audio_response.content)
    
    print(f"✅ Audio saved as {audio_filename}")
    return Response(content=build_recording_response(), media_type="application/xml")
