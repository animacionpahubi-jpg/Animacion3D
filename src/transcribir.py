"""Transcribe la voz de un clip con la API de Gemini (gratis) para revisar idioma, texto, voz y momento en que habla.
Uso: python src/transcribir.py pruebas/ia/NOMBRE.mp4   (clave GEMINI_API_KEY del .env del 3D o del 2D, solo lectura)"""
import base64, json, pathlib, subprocess, sys, urllib.request
import imageio_ffmpeg
RAIZ = pathlib.Path(__file__).resolve().parents[1]
def env(k):
    for f in (RAIZ / ".env", RAIZ.parent / "ANIMACION-2D" / ".env"):
        if f.exists():
            for l in f.read_text(encoding="utf-8").splitlines():
                if l.startswith(k + "="): return l.split("=", 1)[1].strip()
v = pathlib.Path(sys.argv[1]); w = v.with_suffix(".wav")
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y", "-i", str(v), "-vn", "-ac", "1", "-ar", "16000", str(w)], check=True)
cuerpo = {"contents": [{"parts": [{"text": "Transcribe exactly every spoken word with approximate start and end seconds, say the language, and describe each voice (adult woman / child, tone). Also list other sounds. Answer in Spanish, brief."},
                                  {"inline_data": {"mime_type": "audio/wav", "data": base64.b64encode(w.read_bytes()).decode()}}]}]}
req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={env('GEMINI_API_KEY')}",
                             data=json.dumps(cuerpo).encode(), headers={"content-type": "application/json"})
sys.stdout.reconfigure(encoding="utf-8")
print(json.loads(urllib.request.urlopen(req, timeout=120).read())["candidates"][0]["content"]["parts"][0]["text"])
