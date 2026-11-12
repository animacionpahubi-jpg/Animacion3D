"""Imagen con FLUX.2 klein 4B en Cloudflare Workers AI (gratis, 10.000 neuronas/día, Apache 2.0) con imágenes de referencia.
Copiado y adaptado de ANIMACION-2D/src/arte/gratis.py (editar_cf). Claves CLOUDFLARE_ACCOUNT_ID y CLOUDFLARE_API_TOKEN: se leen del .env
del 3D o, si no están, del .env del 2D (solo lectura). Nunca se imprimen.
Uso: python src/flux_cf.py SALIDA.png "prompt" ref1.png [ref2.png ...] [--ancho 768 --alto 1344]"""
import base64, io, json, pathlib, sys, urllib.error, urllib.request, uuid

RAIZ = pathlib.Path(__file__).resolve().parents[1]
MODELO = "@cf/black-forest-labs/flux-2-klein-4b"


def env(k):
    for f in (RAIZ / ".env", RAIZ.parent / "ANIMACION-2D" / ".env"):
        if f.exists():
            for l in f.read_text(encoding="utf-8").splitlines():
                if l.strip().startswith(k + "="): return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"Falta {k} en .env")


def generar(salida, prompt, refs, ancho=768, alto=1344):
    b = uuid.uuid4().hex; out = io.BytesIO(); CRLF = "\r\n"
    for k, v in {"prompt": prompt, "width": str(ancho), "height": str(alto)}.items():
        out.write(f'--{b}{CRLF}Content-Disposition: form-data; name="{k}"{CRLF}{CRLF}{v}{CRLF}'.encode())
    for i, r in enumerate(refs):
        from PIL import Image
        im = Image.open(r).convert("RGB"); im.thumbnail((1024, 1024)); buf = io.BytesIO(); im.save(buf, "PNG")
        out.write(f'--{b}{CRLF}Content-Disposition: form-data; name="input_image_{i}"; filename="ref{i}.png"{CRLF}Content-Type: image/png{CRLF}{CRLF}'.encode()
                  + buf.getvalue() + CRLF.encode())
    out.write(f"--{b}--{CRLF}".encode())
    url = f"https://api.cloudflare.com/client/v4/accounts/{env('CLOUDFLARE_ACCOUNT_ID')}/ai/run/{MODELO}"
    req = urllib.request.Request(url, data=out.getvalue(), headers={"authorization": f"Bearer {env('CLOUDFLARE_API_TOKEN')}",
                                                                     "content-type": f"multipart/form-data; boundary={b}"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r: d = json.loads(r.read())
    except urllib.error.HTTPError as e: sys.exit(f"Cloudflare respondió {e.code}: {e.read().decode(errors='replace')[:400]}")
    pathlib.Path(salida).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(salida).write_bytes(base64.b64decode(d["result"]["image"])); print("ok", salida)


if __name__ == "__main__":
    a = sys.argv[1:]; op = lambda k, d: int(a[a.index(k) + 1]) if k in a else d
    refs = [x for x in a[2:] if not x.startswith("--") and not x.isdigit()]
    generar(a[0], a[1], refs, op("--ancho", 768), op("--alto", 1344))
