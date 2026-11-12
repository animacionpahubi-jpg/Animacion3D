"""Montaje del mini capítulo 3D «¡Atrapa la gota!» (~15 s, vertical 1080x1920, 24 fps).
El título (estilo del logo Pahubi: Fredoka Bold morado con relieve y borde crema) aparece sobre el inicio del plano 2, sin plano
estático. Plano 2 y 3: Kling 3.0 Pro (pruebas/ia/cap1-plano2-caida.mp4, cap1-plano3-rie.mp4); el 3 se corta al empezar la risa
para no mostrar el chorrito de agua que sigue saliendo del pico, con un congelado corto que se funde. Audio sintetizado (src/audio_kit.py, propio) y normalizado a −18 LUFS / pico ≤ −2,5 dBTP.
Uso: python src/montaje_cap1.py  → capitulos/cap1-atrapa-la-gota/cap1-atrapa-la-gota.mp4"""
import pathlib, subprocess, sys, json
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
FF = imageio_ffmpeg.get_ffmpeg_exe()
REF = RAIZ / "personajes" / "referencias"
IA = RAIZ / "pruebas" / "ia"
SAL = RAIZ / "capitulos" / "cap1-atrapa-la-gota"; SAL.mkdir(parents=True, exist_ok=True)
TMP = SAL / "tmp"; TMP.mkdir(exist_ok=True)
FPS, W, H = 24, 1080, 1920
T_TITULO, T_P2, T_P3, T_FIN = 0.0, 5.04, 3.4, 0.9    # T_TITULO=0: el título va encima del plano 2
GOLPE = 2.9                                            # s del plano 3 en que la gota toca el pico


def ff(*a): subprocess.run([FF, "-v", "error", "-y", *a], check=True)


# --- 1. título con el estilo del logo Pahubi --------------------------------------------------------
MORADO, RELIEVE, CREMA = (147, 62, 143), (99, 41, 131), (254, 251, 229)        # colores de logo-pahubi.svg
fuente = ImageFont.truetype(str(RAIZ / "assets" / "fuentes" / "Fredoka.ttf"), 150)
try: fuente.set_variation_by_axes([700, 100])                                  # Fredoka Bold (la fuente es variable)
except Exception: pass
tarjeta = Image.new("RGBA", (W, H), (0, 0, 0, 0))
PROF, BORDE = 10, 14
for i, linea in enumerate(["¡ATRAPA", "LA GOTA!"]):
    d = ImageDraw.Draw(tarjeta); caja = d.textbbox((0, 0), linea, font=fuente, stroke_width=BORDE)
    x = (W - (caja[2] - caja[0])) // 2 - caja[0]; y = 230 + i * 175
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).text((x + 8, y + PROF + 12), linea, font=fuente, fill=(40, 10, 50, 140), stroke_width=BORDE, stroke_fill=(40, 10, 50, 140))
    tarjeta = Image.alpha_composite(tarjeta, sombra.filter(ImageFilter.GaussianBlur(10))); d = ImageDraw.Draw(tarjeta)
    for k in range(PROF + 1): d.text((x + k * .5, y + k), linea, font=fuente, fill=CREMA, stroke_width=BORDE, stroke_fill=CREMA)   # borde crema
    for k in range(1, PROF + 1): d.text((x + k * .5, y + k), linea, font=fuente, fill=RELIEVE)                                 # relieve
    d.text((x, y), linea, font=fuente, fill=MORADO)
tarjeta.save(TMP / "titulo.png")

# plano 2 con el título encima (entra con un pequeño salto y se va antes de la picada)
ff("-i", str(IA / "cap1-plano2-caida.mp4"), "-loop", "1", "-i", str(TMP / "titulo.png"),
   "-filter_complex", f"[0]scale={W}:{H},fps={FPS}[v];[1]format=rgba,fade=t=in:st=0.15:d=0.35:alpha=1,fade=t=out:st=2.0:d=0.4:alpha=1[t];"
   "[v][t]overlay=0:'-40*exp(-8*t)*cos(14*t)':shortest=1,format=yuv420p[o]",
   "-map", "[o]", "-t", str(T_P2), "-an", "-c:v", "libx264", "-crf", "16", str(TMP / "p2.mp4"))
# plano 3 cortado justo al empezar la risa + congelado corto que se funde a negro
ff("-t", str(T_P3), "-i", str(IA / "cap1-plano3-rie.mp4"), "-vf", f"scale={W}:{H},fps={FPS},"
   f"tpad=stop_mode=clone:stop_duration={T_FIN},fade=t=out:st={T_P3 + T_FIN - 0.6}:d=0.6,format=yuv420p",
   "-an", "-c:v", "libx264", "-crf", "16", str(TMP / "p3.mp4"))
(TMP / "lista.txt").write_text("".join(f"file '{(TMP / p).as_posix()}'\n" for p in ("p2.mp4", "p3.mp4")), encoding="utf-8")
ff("-f", "concat", "-safe", "0", "-i", str(TMP / "lista.txt"), "-c", "copy", str(TMP / "video.mp4"))

# --- 2. audio sintetizado ---------------------------------------------------------------------------
from audio_kit import SR, piano, mbox, pluckn, fq, flapf, whoosh, mud, phrase, dropb, lp, tt
DUR = T_TITULO + T_P2 + T_P3 + T_FIN; n = int(SR * DUR); a = np.zeros(n)
def pon(x, t, g=1.0):
    i = int(t * SR)
    if 0 <= i < n: x = x[: n - i]; a[i:i + len(x)] += x * g
# música: «curioso» en el título y la persecución, «cómico» en el remate
t, k = 0.1, 0
for nota in ["E5", "G5", "A5", "C6", "A5", "G5", "E5", "G5", "A5", "C6", "D6", "C6", "A5", "G5"]:
    if t > T_TITULO + 3.6: break
    pon(mbox(fq(nota), 1.2, .08), t); t += .62
t = T_TITULO + T_P2 + .1
for nota in ["C4", "G4", "E4", "G4", "D4", "A4", "F4", "A4", "C5", "G4"]:
    if t > DUR - .6: break
    pon(pluckn(fq(nota), .45, .085), t); t += .5
pon(piano(fq("C5"), 1.8, .1), DUR - 1.2); pon(piano(fq("E5"), 1.8, .08), DUR - 1.2); pon(piano(fq("G5"), 1.8, .07), DUR - 1.2)
# efectos
for i, nt in enumerate(["C6", "E6", "G6"]): pon(mbox(fq(nt), 1.2, .07), 0.35 + i * .12)          # brillo del título
t0 = T_TITULO
for x in np.arange(t0, t0 + 2.6, 1 / 12): pon(flapf(.05), x)                                         # aleteo
pon(whoosh(1.0, .07, 300, 1500), t0 + 2.3)                                                            # picada
pon(mud(.28), t0 + 3.35)                                                                              # ¡splash! en el barro
pon(phrase(2600, 2, .05, 5), t0 + 3.8)                                                                # «¿eh?»
t0 = T_TITULO + T_P2
pon(dropb(.06), t0 + GOLPE)                                                # ¡plip! en el pico
for i in range(4): pon(phrase(2800 + 120 * i, 2, .05, 11 + i), t0 + GOLPE + .25 + i * .28)                    # risita
a *= np.clip(np.minimum(tt(DUR) / .3, (DUR - tt(DUR)) / .8), 0, 1)[:n]
a = lp(a, 7500, 4)
import scipy.io.wavfile as wv
wv.write(TMP / "audio_raw.wav", SR, (a / (np.max(np.abs(a)) + 1e-9) * 0.7 * 32767).astype(np.int16))
ff("-i", str(TMP / "audio_raw.wav"), "-af", "loudnorm=I=-17.4:TP=-2.5:LRA=7", "-ar", "44100", str(TMP / "audio.wav"))

# --- 3. unir y medir --------------------------------------------------------------------------------
final = SAL / "cap1-atrapa-la-gota.mp4"
ff("-i", str(TMP / "video.mp4"), "-i", str(TMP / "audio.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
   "-shortest", "-movflags", "+faststart", str(final))
r = subprocess.run([FF, "-hide_banner", "-i", str(final), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
resumen = r.stderr[r.stderr.rfind("Summary:"):]
print(resumen)
print("LISTO", final)
