"""Un plano con Kling 3.0 Pro (imagen a video, 1080p, sin audio) amarrado a imagen inicial y final — Pahubi Animación 3D.
Inicio y final fijos + prohibiciones explícitas = menos inconsistencias (alas de insecto, pico que cambia, objetos que aparecen).
Uso: python src/fal_kling_plano.py NOMBRE inicio.png [final.png|-] "prompt" [--segundos 5]
Costo: 0,112 USD/s (5 s ≈ 0,56 USD). Salida: pruebas/ia/NOMBRE.mp4 + .json; gasto en config/fal_gasto.json."""
import json, pathlib, sys, time, urllib.request
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fal_imagen import clave, pedir, GASTO, TOPE_USD
from fal_video import subir

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SAL = RAIZ / "pruebas" / "ia"
RUTA = "fal-ai/kling-video/v3/pro/image-to-video"
POR_SEG = 0.112
NEGATIVO = ("transparent wings, insect wings, bee wings, dragonfly wings, curved beak, beak changing length, hat changing, extra limbs, "
            "extra characters, duplicate character, floating objects, objects appearing from nowhere, scene cut, jump cut, camera cut, "
            "crest changing, feathers appearing, continuous water spray, water stream from beak, mud appearing or disappearing suddenly, morphing, deformed face, distorted, blurry character, text, subtitles, watermark, logo")
ESTILO = (" Keep every character exactly as in the start and end images the whole time. Baby hummingbird: same knitted purple striped "
          "beanie with pompom, the crest is always the same three green leaf feathers at the front-left under the beanie edge (never on top, "
          "never appearing or disappearing), same long thin straight slate-blue beak, pink feathered wings, purple feet. Mom hummingbird (if "
          "present) stays bigger than the baby. Continuous single shot, no cuts. Drops always fall down with gravity, never float. "
          "High-end 3D animated feature film quality, golden sunrise light.")


def generar(nombre, inicio, final, prompt, segundos=5):
    g = json.loads(GASTO.read_text(encoding="utf-8")) if GASTO.exists() else {"usd": 0.0, "imagenes": []}
    costo = round(POR_SEG * segundos, 3)
    if g["usd"] + costo > TOPE_USD: sys.exit(f"Tope del 3D alcanzado (${g['usd']:.2f} de ${TOPE_USD:.2f})")
    k = clave()
    cuerpo = {"prompt": prompt + ESTILO, "negative_prompt": NEGATIVO, "start_image_url": subir(inicio, "image/png"),
              "duration": str(segundos), "generate_audio": False}
    if final: cuerpo["end_image_url"] = subir(final, "image/png")
    t = pedir(f"https://queue.fal.run/{RUTA}", cuerpo, k)
    for _ in range(400):
        if pedir(t["status_url"], k=k).get("status") == "COMPLETED": break
        time.sleep(6)
    res = pedir(t["response_url"], k=k)
    SAL.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(res["video"]["url"], timeout=300) as r: (SAL / f"{nombre}.mp4").write_bytes(r.read())
    meta = {"nombre": nombre, "modelo": RUTA, "inicio": str(inicio), "final": str(final) if final else None, "prompt": cuerpo["prompt"],
            "negativo": NEGATIVO, "segundos": segundos, "usd_aprox": costo, "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (SAL / f"{nombre}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    g["usd"] = round(g["usd"] + costo, 4); g.setdefault("videos", []).append({"nombre": nombre, "modelo": RUTA, "usd": costo, "fecha": meta["fecha"]})
    GASTO.write_text(json.dumps(g, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ok {SAL / (nombre + '.mp4')} (~${costo:.2f}; gastado 3D ~${g['usd']:.2f})")


if __name__ == "__main__":
    a = sys.argv[1:]
    generar(a[0], pathlib.Path(a[1]), None if a[2] == "-" else pathlib.Path(a[2]), a[3],
            int(a[a.index("--segundos") + 1]) if "--segundos" in a else 5)
