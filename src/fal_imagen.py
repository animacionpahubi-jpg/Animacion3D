"""Imágenes con el modelo de ChatGPT (GPT Image 2.6) vía fal.ai — Pahubi Animación 3D.
La clave FAL_KEY se toma de Animacion-3D/.env si existe; si no, se LEE (sin modificarlo) del .env de ANIMACION-2D.
El gasto del 3D se anota aparte en Animacion-3D/config/fal_gasto.json (tope en TOPE_USD).
Uso: python src/fal_imagen.py NOMBRE "prompt" ref1.png[,ref2.png,...] [--calidad high] [--tamano landscape_16_9]
Salida: personajes/generadas/NOMBRE.png + NOMBRE.json"""
import base64, io, json, pathlib, sys, time, urllib.request
from datetime import datetime, timezone
from PIL import Image

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SAL = RAIZ / "personajes" / "generadas"
GASTO = RAIZ / "config" / "fal_gasto.json"
MODELO = "openai/gpt-image-2.6/sunburst/edit"
COSTO_APROX = {"low": 0.03, "medium": 0.10, "high": 0.30, "xhigh": 0.45, "max": 0.60}   # USD por imagen 16:9 (estimado)
TOPE_USD = 10.0


def clave():
    for env in (RAIZ / ".env", RAIZ.parent / "ANIMACION-2D" / ".env"):
        if env.exists():
            for l in env.read_text(encoding="utf-8").splitlines():
                if l.startswith("FAL_KEY="): return l.split("=", 1)[1].strip().strip('"')
    sys.exit("No encontré FAL_KEY")


def data_uri(p, lado=1536):
    im = Image.open(p).convert("RGB"); im.thumbnail((lado, lado), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def pedir(url, cuerpo=None, k=None):
    cab = {"Authorization": f"Key {k}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(cuerpo).encode() if cuerpo is not None else None, headers=cab)
    with urllib.request.urlopen(req, timeout=180) as r: return json.load(r)


def generar(nombre, prompt, refs, calidad="high", tamano="landscape_16_9"):
    g = json.loads(GASTO.read_text(encoding="utf-8")) if GASTO.exists() else {"usd": 0.0, "imagenes": []}
    costo = COSTO_APROX[calidad]
    if g["usd"] + costo > TOPE_USD: sys.exit(f"Tope del 3D alcanzado (${g['usd']:.2f} de ${TOPE_USD:.2f})")
    k = clave()
    cuerpo = {"prompt": prompt, "image_urls": [data_uri(r) for r in refs], "quality": calidad, "image_size": tamano,
              "output_format": "png", "num_images": 1}
    t = pedir(f"https://queue.fal.run/{MODELO}", cuerpo, k)
    for _ in range(180):
        st = pedir(t["status_url"], k=k)
        if st.get("status") == "COMPLETED": break
        time.sleep(4)
    res = pedir(t["response_url"], k=k)
    url = res["images"][0]["url"]
    SAL.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as r: (SAL / f"{nombre}.png").write_bytes(r.read())
    meta = {"nombre": nombre, "modelo": MODELO, "calidad": calidad, "tamano": tamano, "refs": [str(r) for r in refs],
            "prompt": prompt, "usd_aprox": costo, "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (SAL / f"{nombre}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    g["usd"] = round(g["usd"] + costo, 4); g["imagenes"].append({"nombre": nombre, "usd": costo, "fecha": meta["fecha"]})
    GASTO.parent.mkdir(parents=True, exist_ok=True); GASTO.write_text(json.dumps(g, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ok {SAL / (nombre + '.png')} (~${costo:.2f}; gastado 3D ~${g['usd']:.2f})")


if __name__ == "__main__":
    a = sys.argv[1:]; op = lambda x, d: a[a.index(x) + 1] if x in a else d
    generar(a[0], a[1], [pathlib.Path(x) for x in a[2].split(",")], op("--calidad", "high"), op("--tamano", "landscape_16_9"))
