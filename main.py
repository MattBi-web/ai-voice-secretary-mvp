from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
import requests
import openai
import os

app = FastAPI()

# CONFIG
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

CACHE_DIR = "/mnt/data/cache_responses"
os.makedirs(CACHE_DIR, exist_ok=True)

# Endpoint iniziale: risponde subito con transizione vocale
@app.post("/voice")
async def voice_entry():
    return Response(content="""<?xml version='1.0' encoding='UTF-8'?>
<Response>
    <Say voice='alice' language='it-IT'>Un secondo che controllo...</Say>
    <Record maxLength='10' action='/process-recording' method='POST' />
</Response>""", media_type="application/xml")

# Endpoint che riceve l'audio e genera la risposta AI
@app.post("/process-recording")
async def handle_recording(RecordingUrl: str = Form(...), From: str = Form(...)):
    print(f"▶️ Ricevuta registrazione da {From}: {RecordingUrl}")
    
    audio_url = RecordingUrl + ".mp3"
    audio_path = f"/mnt/data/from_{From.replace('+','')}.mp3"
    r = requests.get(audio_url)
    with open(audio_path, "wb") as f:
        f.write(r.content)

    # Trascrizione con Whisper API
    with open(audio_path, "rb") as f:
        transcript = openai.Audio.transcribe("whisper-1", f)
    user_text = transcript["text"]
    print(f"🗣 Utente ha detto: {user_text}")

    # GPT-3.5 genera la risposta
    prompt = f"Sei una segreteria vocale per un ristorante. Rispondi in modo cordiale e utile. Il cliente ha detto: '{user_text}'"
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    reply_text = completion["choices"][0]["message"]["content"]
    print(f"🤖 Risposta GPT: {reply_text}")

    # Controlla se esiste già audio per quella risposta (cache)
    from hashlib import sha1
    hashname = sha1(reply_text.encode()).hexdigest()
    cached_audio = os.path.join(CACHE_DIR, f"{hashname}.mp3")

    if not os.path.exists(cached_audio):
        print("🎙 Genero audio con ElevenLabs")
        tts_response = requests.post(
            "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL",  # ID voce predefinita
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": reply_text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
            }
        )
        with open(cached_audio, "wb") as out:
            out.write(tts_response.content)
        print("✅ Audio salvato in cache")
    else:
        print("💾 Audio già in cache")

    # TwiML per far ascoltare la risposta
    return Response(content=f"""<?xml version='1.0' encoding='UTF-8'?>
<Response>
    <Play>{cached_audio.replace('/mnt/data','https://ai-voice-secretary-mvp.onrender.com/static')}</Play>
</Response>""", media_type="application/xml")
