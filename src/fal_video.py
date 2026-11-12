"""Fase 1.3: pintar una guía de movimiento de Blender con IA de video (fal.ai) usando la hoja oficial del personaje.
Modelos:
  wan480   alibaba/wan-3.0/reference-to-video, 480p          (~0,05 USD/s) — económico
  kling    fal-ai/kling-video/o3/standard/video-to-video/reference, 720p (~0,126 USD/s) — normal
  mini480  bytedance/seedance-2.0/mini/reference-to-video, 480p (~0,40 USD por 5 s con la guía) — el mismo que da Higgsfield Starter
  seedance480  bytedance/seedance-2.5/us/reference-to-video, tarea «editing», borrador 480p (~1,23 USD por 5 s con la guía) — método del video 3
Uso: python src/fal_video.py MODELO guia.mp4 NOMBRE [--segundos 5]
Salida: pruebas/ia/NOMBRE.mp4 + NOMBRE.json. Gasto en config/fal_gasto.json (mismo tope que las imágenes)."""
import json, pathlib, sys, time, urllib.request
from datetime import datetime, timezone
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fal_imagen import clave, pedir, GASTO, TOPE_USD

RAIZ = pathlib.Path(__file__).resolve().parents[1]
HOJAS = RAIZ / "personajes" / "hojas"
SAL = RAIZ / "pruebas" / "ia"
POR_SEG = {"wan480": 0.05, "kling": 0.126, "seedance480": 0.246, "mini480": 0.08}   # seedance: (entrada+salida) con descuento por video ≈ 1,23 USD / 5 s

PROMPT = ("Cinematic 3D animated feature film shot, high-end animation studio quality. {ref} keep his exact design: round lime-green plush body "
          "with creamy yellow belly, purple knitted beanie with lighter horizontal stripes and a fluffy purple pompom, two or three small green "
          "leaf-shaped crest feathers, big eyes with dark purple irises and two highlights, pink cheeks, thin straight slate-blue beak, pink wings, "
          "purple feet. Follow EXACTLY the motion, timing, positions and camera movement of {vid}: he flies in from the top right with very fast "
          "hummingbird wing beats, slows down, hovers behind the edge of a big glossy green leaf in the foreground, then lowers and peeks over the "
          "leaf edge with his beak toward a big clear dew drop on the leaf, curious and happy. Golden sunrise backlight with the sun in the upper "
          "right, warm sun rays through a lush tropical jungle, soft morning mist, shallow depth of field with warm bokeh, tiny dew droplets "
          "sparkling on the leaf and its veins. Replace the simple blockout shapes with rich, detailed materials. No text, no extra characters.")


PROMPT_EDICION = ("@Video1 is a gray clay previz (blockout) of a 3D animated film shot. Repaint it into the final high-end 3D animated feature "
    "film shot, keeping EXACTLY the same camera movement, timing, positions, silhouettes and motion physics. The gray bird is the baby hummingbird "
    "from @Image1 (face close-up) and @Image2 (character sheet): give him exactly that design - round lime-green plush body with soft fine "
    "feathers, creamy yellow belly, purple knitted beanie with lighter horizontal stripes and a fluffy purple pompom, two or three small green "
    "leaf-shaped crest feathers, big expressive eyes with dark purple irises and two highlights, pink cheeks, short straight slate-blue beak "
    "exactly as long as in @Image1, pink wings with lilac tips, purple feet. He is alive and expressive: blinks, curious happy face, "
    "very fast blurred hummingbird wing beats while flying, gentle breathing while he peeks. The gray foreground shape is a big glossy "
    "tropical leaf with visible veins covered in tiny sparkling dew droplets; the gray ball on it is a big clear dew drop that refracts the "
    "light. The gray background blobs are a lush tropical jungle. Golden sunrise backlight from the upper right, warm sun rays through the "
    "mist, rim light on the feathers, shallow depth of field with warm bokeh. No text, no extra characters.")


def subir(ruta, tipo):
    """Sube un archivo al almacenamiento de fal y devuelve su URL."""
    k = clave()
    ini = pedir("https://rest.alpha.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3",
                {"content_type": tipo, "file_name": pathlib.Path(ruta).name}, k)
    req = urllib.request.Request(ini["upload_url"], data=pathlib.Path(ruta).read_bytes(), method="PUT", headers={"Content-Type": tipo})
    urllib.request.urlopen(req, timeout=300).read()
    return ini["file_url"]


def cara_bebe():
    """Primer plano de la cara (sección 1 de la hoja) como imagen frontal del personaje."""
    p = SAL / "_bebe-cara.png"
    if not p.exists():
        im = Image.open(HOJAS / "bebe-hoja-original.png"); SAL.mkdir(parents=True, exist_ok=True)
        im.crop((0, 0, im.width // 3 - 4, im.height)).save(p)
    return p


def generar(modelo, guia, nombre, segundos=5):
    g = json.loads(GASTO.read_text(encoding="utf-8")) if GASTO.exists() else {"usd": 0.0, "imagenes": []}
    costo = round(POR_SEG[modelo] * segundos, 3)
    if g["usd"] + costo > TOPE_USD: sys.exit(f"Tope del 3D alcanzado (${g['usd']:.2f} de ${TOPE_USD:.2f})")
    k = clave()
    v = subir(guia, "video/mp4"); hoja = subir(HOJAS / "bebe-hoja.png", "image/png"); cara = subir(cara_bebe(), "image/png")
    if modelo == "kling":
        ruta = "fal-ai/kling-video/o3/standard/video-to-video/reference"
        cuerpo = {"prompt": PROMPT.format(ref="The baby hummingbird @Element1:", vid="@Video1"), "video_url": v,
                  "elements": [{"frontal_image_url": cara, "reference_image_urls": [hoja]}],
                  "duration": str(segundos), "aspect_ratio": "9:16", "keep_audio": False}
    elif modelo == "mini480":
        ruta = "bytedance/seedance-2.0/mini/reference-to-video"
        cuerpo = {"prompt": PROMPT_EDICION, "video_urls": [v], "image_urls": [cara, hoja], "resolution": "480p",
                  "aspect_ratio": "9:16", "duration": str(segundos), "generate_audio": False}
    elif modelo == "seedance480":
        ruta = "bytedance/seedance-2.5/us/reference-to-video"
        cuerpo = {"prompt": PROMPT_EDICION, "video_urls": [v], "image_urls": [cara, hoja], "task": "editing",
                  "draft": True, "resolution": "480p", "generate_audio": False}
    else:
        ruta = "alibaba/wan-3.0/reference-to-video"
        cuerpo = {"prompt": PROMPT.format(ref="The baby hummingbird shown in Image 1 (face close-up) and Image 2 (character sheet):", vid="Video 1"),
                  "reference_image_urls": [cara, hoja], "reference_video_urls": [v], "resolution": "480p", "aspect_ratio": "9:16",
                  "duration": segundos, "audio": False}
    t = pedir(f"https://queue.fal.run/{ruta}", cuerpo, k)
    for _ in range(400):
        st = pedir(t["status_url"], k=k)
        if st.get("status") == "COMPLETED": break
        time.sleep(6)
    res = pedir(t["response_url"], k=k)
    url = (res.get("video") or {}).get("url") or res.get("videos", [{}])[0].get("url")
    if res.get("draft_id"): print("draft_id (para terminar en 1080p dentro de 7 días):", res["draft_id"]); cuerpo["draft_id_resultado"] = res["draft_id"]
    SAL.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=300) as r: (SAL / f"{nombre}.mp4").write_bytes(r.read())
    meta = {"nombre": nombre, "modelo": ruta, "guia": str(guia), "segundos": segundos, "usd_aprox": costo,
            "cuerpo": {k2: v2 for k2, v2 in cuerpo.items()}, "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (SAL / f"{nombre}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    g["usd"] = round(g["usd"] + costo, 4); g.setdefault("videos", []).append({"nombre": nombre, "modelo": ruta, "usd": costo, "fecha": meta["fecha"]})
    GASTO.write_text(json.dumps(g, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ok {SAL / (nombre + '.mp4')} (~${costo:.2f}; gastado 3D ~${g['usd']:.2f})")


if __name__ == "__main__":
    a = sys.argv[1:]
    generar(a[0], pathlib.Path(a[1]), a[2], int(a[a.index("--segundos") + 1]) if "--segundos" in a else 5)
