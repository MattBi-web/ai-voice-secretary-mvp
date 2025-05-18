def build_twiml_response():
    return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="it-IT">Ciao! La segreteria vocale è attiva. Parla pure dopo il bip.</Say>
    <Record maxLength="20" action="/handle-recording" method="POST" />
    <Say>Grazie per aver chiamato. A presto!</Say>
</Response>"""