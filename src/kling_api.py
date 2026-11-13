"""Un plano con la API oficial de Kling (imagen inicial + imagen final) — Pahubi Animación 3D.
Clave: KLING_API_KEY en Animacion-3D/.env (nunca se imprime). Servidor global api-singapore.klingai.com.
Uso: python src/kling_api.py NOMBRE inicio.png final.png|- "prompt" [--segundos 5|10] [--modelo kling-v3] [--modo pro]
Salida: pruebas/ia/NOMBRE.mp4 + NOMBRE.json; registro en config/kling_gasto.json."""
import base64, json, pathlib, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SAL = RAIZ / "pruebas" / "ia"
REG = RAIZ / "config" / "kling_gasto.json"
API = "https://api-singapore.klingai.com"
NEGATIVO = ("transparent wings, insect wings, teal wings, turquoise wings, green wings, blue tail, peacock tail, blue feathers, stretched drop, liquid string, gooey drop, drop hanging on a thread, spider thread, "
            "water streams like threads, mud growing, beak touching the face, curved beak, short beak, beak changing length, hat changing color, crest coming out of the hat fabric, crest on top of the beanie, leaves growing through the hat, tall crest, more than three crest leaves, "
            "crest on the side, fan crest, spiky crest, slick helmet hair, mom same size as baby, extra feathers, extra limbs, extra characters, duplicate character, floating drops, drops hovering, objects appearing "
            "from nowhere, mud spots multiplying, beak poking into the other character, scene cut, jump cut, morphing, deformed face, blurry, text, watermark, logo")
ESTILO = (" Keep both characters exactly as in the start and end images the whole time: the baby's magenta striped knitted beanie with the pompom at the "
          "back, his exactly three SHORT thin green leaf feathers growing from his forehead under the front brim of the beanie (never on top of it), his long thin straight navy-blue beak; "
          "mom (if present) with her crest of 5-6 separate matte leaf feathers swept back, always clearly bigger than the baby (about 1.4x). Drops always fall with gravity. Continuous single shot, "
          "high-end 3D animated feature film quality, warm golden sunrise backlight, saturated warm colors, smooth fluid animation.")


def clave():
    for l in (RAIZ / ".env").read_text(encoding="utf-8").splitlines():
        if l.startswith("KLING_API_KEY="): return l.split("=", 1)[1].strip()
    sys.exit("Falta KLING_API_KEY en Animacion-3D/.env")


def pedir(ruta, cuerpo=None):
    req = urllib.request.Request(API + ruta, data=json.dumps(cuerpo).encode() if cuerpo is not None else None,
                                 method="POST" if cuerpo is not None else "GET",
                                 headers={"Authorization": "Bearer " + clave(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b"{}") | {"http": e.code}


def b64(p): return base64.b64encode(pathlib.Path(p).read_bytes()).decode()


def generar(nombre, inicio, final, prompt, segundos=5, modelo="kling-v3", modo="pro", sonido="off"):
    cuerpo = {"model_name": modelo, "mode": modo, "image": b64(inicio), "prompt": prompt + ESTILO, "negative_prompt": NEGATIVO,
              "cfg_scale": 0.5, "duration": str(segundos), "sound": sonido}
    if final: cuerpo["image_tail"] = b64(final)
    r = pedir("/v1/videos/image2video", cuerpo)
    if r.get("code") != 0: sys.exit(f"Kling rechazó la tarea: {json.dumps(r, ensure_ascii=False)[:500]}")
    tid = r["data"]["task_id"]; print("tarea", tid, flush=True)
    for _ in range(240):
        time.sleep(10)
        e = pedir(f"/v1/videos/image2video/{tid}")
        st = (e.get("data") or {}).get("task_status")
        if st == "succeed": break
        if st == "failed": sys.exit(f"Kling falló: {json.dumps(e, ensure_ascii=False)[:500]}")
    else: sys.exit("Tiempo de espera agotado")
    url = e["data"]["task_result"]["videos"][0]["url"]
    SAL.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=300) as v: (SAL / f"{nombre}.mp4").write_bytes(v.read())
    meta = {"nombre": nombre, "modelo": modelo, "modo": modo, "sonido": sonido, "segundos": segundos, "inicio": str(inicio), "final": str(final) if final else None,
            "prompt": cuerpo["prompt"], "task_id": tid, "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (SAL / f"{nombre}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    g = json.loads(REG.read_text(encoding="utf-8")) if REG.exists() else {"tareas": []}
    g["tareas"].append({k: meta[k] for k in ("nombre", "modelo", "modo", "segundos", "task_id", "fecha")})
    REG.write_text(json.dumps(g, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ok", SAL / f"{nombre}.mp4")


if __name__ == "__main__":
    a = sys.argv[1:]
    op = lambda k, d: a[a.index(k) + 1] if k in a else d
    generar(a[0], pathlib.Path(a[1]), None if a[2] == "-" else pathlib.Path(a[2]), a[3],
            int(op("--segundos", 5)), op("--modelo", "kling-v3"), op("--modo", "pro"), op("--sonido", "off"))
