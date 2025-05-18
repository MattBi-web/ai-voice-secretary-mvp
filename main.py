from fastapi import FastAPI, Request
from fastapi.responses import Response
from twiml_response import build_twiml_response

app = FastAPI()

@app.post("/voice")
async def voice_response(request: Request):
    twiml = build_twiml_response()
    return Response(content=twiml, media_type="application/xml")