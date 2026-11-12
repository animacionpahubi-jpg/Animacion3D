"""Montaje de «¡Atrapa la gota!» v5 — 3 planos Kling 3.0 Pro (API oficial) sobre las imágenes clave de cap1-gota-v5 (Codex).
Guion: A) ve la gota, se suelta y él se lanza en picada hasta caer al charco · B) una gota de la flor le cae en el pico, se ríe y llega
mamá · C) mamá lo abraza aunque esté embarrado.
Recortes (lecciones-kling.md, regla 6): B sin 3.8–4.75 s (la gota se estira como hilo) · C sin 4.2–5.0 s (pico de mamá toca el gorro).
Kling entrega 1176x1764 (2:3): se escala a 1920 de alto (1280 de ancho) y se recorta a 1080 con desplazamiento X por plano.
Título estilo logo Pahubi. Audio sintetizado propio (src/audio_kit.py) a −18 LUFS, pico ≤ −2,5 dBTP.
Uso: python src/montaje_cap1v5.py → capitulos/cap1-atrapa-la-gota/cap1-atrapa-la-gota-v5.mp4"""
import pathlib, subprocess, sys
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
FF = imageio_ffmpeg.get_ffmpeg_exe()
IA = RAIZ / "pruebas" / "ia"
SAL = RAIZ / "capitulos" / "cap1-atrapa-la-gota"; SAL.mkdir(parents=True, exist_ok=True)
TMP = SAL / "tmp5"; TMP.mkdir(exist_ok=True)
FPS, W, H, XF, HOLD = 24, 1080, 1920, 0.25, 1.0
# tramos: (archivo, desde, hasta, desplazamiento X del recorte en 1280, ¿fundido con el anterior?)
TRAMOS = [("cap1-A3", 0.0, 5.0, 0, False),
          ("cap1-B2", 0.0, 3.8, 60, False), ("cap1-B2", 4.75, 10.0, 60, True),
          ("cap1-C2", 0.0, 4.2, 60, False), ("cap1-C2", 5.0, 10.0, 60, True)]


def ff(*a): subprocess.run([FF, "-v", "error", "-y", *a], check=True)


# inicio de cada tramo en la línea de tiempo final
INI = []; t = 0.0
for i, (_, a, b, _, fx) in enumerate(TRAMOS):
    if fx: t -= XF
    INI.append(t); t += b - a
DUR = t + HOLD


def T(tramo, seg):
    """Tiempo final de un momento medido en el clip original (segundo `seg` del archivo del tramo)."""
    return INI[tramo] + seg - TRAMOS[tramo][1]


# --- título (estilo logo Pahubi) ------------------------------------------------------------------------
MORADO, RELIEVE, CREMA = (147, 62, 143), (99, 41, 131), (254, 251, 229)
fuente = ImageFont.truetype(str(RAIZ / "assets" / "fuentes" / "Fredoka.ttf"), 150)
try: fuente.set_variation_by_axes([700, 100])
except Exception: pass
tarjeta = Image.new("RGBA", (W, H), (0, 0, 0, 0)); PROF, BORDE = 10, 14
for i, linea in enumerate(["¡ATRAPA", "LA GOTA!"]):
    d = ImageDraw.Draw(tarjeta); caja = d.textbbox((0, 0), linea, font=fuente, stroke_width=BORDE)
    x = (W - (caja[2] - caja[0])) // 2 - caja[0]; y = 1440 + i * 175
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).text((x + 8, y + PROF + 12), linea, font=fuente, fill=(40, 10, 50, 140), stroke_width=BORDE, stroke_fill=(40, 10, 50, 140))
    tarjeta = Image.alpha_composite(tarjeta, sombra.filter(ImageFilter.GaussianBlur(10))); d = ImageDraw.Draw(tarjeta)
    for k in range(PROF + 1): d.text((x + k * .5, y + k), linea, font=fuente, fill=CREMA, stroke_width=BORDE, stroke_fill=CREMA)
    for k in range(1, PROF + 1): d.text((x + k * .5, y + k), linea, font=fuente, fill=RELIEVE)
    d.text((x, y), linea, font=fuente, fill=MORADO)
tarjeta.save(TMP / "titulo.png")

# --- video ----------------------------------------------------------------------------------------------
partes = []
for i, (nom, a, b, dx, _) in enumerate(TRAMOS):
    v = f"[0]scale=1280:{H}:flags=lanczos,crop={W}:{H}:{dx}:0,fps={FPS},setpts=PTS-STARTPTS"
    src = ["-ss", str(a), "-t", str(b - a), "-i", str(IA / f"{nom}.mp4")]
    if i == 0:
        ff(*src, "-loop", "1", "-i", str(TMP / "titulo.png"), "-filter_complex",
           v + "[v];[1]format=rgba,fade=t=in:st=0.1:d=0.35:alpha=1,fade=t=out:st=2.4:d=0.4:alpha=1[t];"
           "[v][t]overlay=0:'-40*exp(-8*t)*cos(14*t)':shortest=1,format=yuv420p[o]", "-map", "[o]",
           "-an", "-c:v", "libx264", "-crf", "16", str(TMP / f"p{i}.mp4"))
    else:
        extra = f",tpad=stop_mode=clone:stop_duration={HOLD},fade=t=out:st={b - a + HOLD - .8:.2f}:d=0.8" if i == len(TRAMOS) - 1 else ""
        ff(*src, "-filter_complex", v + extra + ",format=yuv420p[o]", "-map", "[o]", "-an", "-c:v", "libx264", "-crf", "16", str(TMP / f"p{i}.mp4"))
    partes.append((TMP / f"p{i}.mp4", b - a + (HOLD if i == len(TRAMOS) - 1 else 0)))
# une: corte directo entre planos (imagen final de uno = inicial del siguiente), fundido corto dentro de un plano recortado
actual, dur = partes[0]
for i in range(1, len(partes)):
    sig, dsig = partes[i]; sal = TMP / f"u{i}.mp4"
    if TRAMOS[i][4]:
        ff("-i", str(actual), "-i", str(sig), "-filter_complex",
           f"[0][1]xfade=transition=fade:duration={XF}:offset={dur - XF},format=yuv420p[o]", "-map", "[o]", "-c:v", "libx264", "-crf", "16", str(sal))
        dur = dur + dsig - XF
    else:
        ff("-i", str(actual), "-i", str(sig), "-filter_complex", "[0][1]concat=n=2:v=1:a=0,format=yuv420p[o]", "-map", "[o]",
           "-c:v", "libx264", "-crf", "16", str(sal))
        dur = dur + dsig
    actual = sal

# --- audio ----------------------------------------------------------------------------------------------
from audio_kit import SR, piano, mbox, pluckn, fq, flapf, whoosh, mud, phrase, dropb, lp, tt
n = int(SR * DUR); au = np.zeros(n)
def pon(x, t, g=1.0):
    i = int(t * SR)
    if 0 <= i < n: x = x[: n - i]; au[i:i + len(x)] += x * g
SUELTA, SALTO, CHAPUZON = T(0, 1.1), T(0, 1.6), T(0, 3.5)
PLIP, LLEGA, ABRAZO = T(2, 4.95), T(2, 5.9), T(4, 5.3)
# música: curiosa hasta el chapuzón, juguetona con la risa, tierna con mamá
t = .1
for nota in ["E5", "G5", "A5", "C6", "A5", "G5", "E5", "G5"]:
    if t > CHAPUZON - .3: break
    pon(mbox(fq(nota), 1.2, .075), t); t += .5
t = CHAPUZON + .5
for nota in ["C4", "G4", "E4", "G4", "D4", "A4", "F4", "A4", "C5", "G4", "E4", "G4", "D4", "A4"]:
    if t > LLEGA - .2: break
    pon(pluckn(fq(nota), .45, .08), t); t += .5
t = LLEGA
while t < DUR - 1.5:
    for acorde in (["C5", "E5", "G5"], ["F4", "A4", "C5"], ["G4", "B4", "D5"], ["F4", "A4", "C5"], ["C5", "E5", "G5"]):
        if t > DUR - 1.5: break
        for j, nota in enumerate(acorde): pon(piano(fq(nota), 2.2, .07 - j * .01), t + j * .04)
        t += 1.6
# efectos y vocecitas
for i, nt in enumerate(["C6", "E6", "G6"]): pon(mbox(fq(nt), 1.2, .07), .2 + i * .12)      # brillo del título
pon(phrase(2700, 2, .04, 3), .5)                                                             # «mmm» con sed
pon(dropb(.05), SUELTA)                                                                       # la gota se suelta
for x in np.arange(SALTO, CHAPUZON - .2, 1 / 12): pon(flapf(.04), x)                          # aleteo
pon(whoosh(1.2, .07, 300, 1500), SALTO + .3)                                                 # picada
pon(mud(.28), CHAPUZON)                                                                       # ¡splash!
pon(phrase(2500, 2, .05, 5), CHAPUZON + .7)                                                  # «¿eh?»
pon(dropb(.06), PLIP)                                                                         # ¡plip! en el pico
for i in range(5): pon(phrase(2800 + 120 * i, 2, .05, 11 + i), PLIP + .3 + i * .26)          # risita
for x in np.arange(LLEGA, LLEGA + 1.6, 1 / 10): pon(flapf(.03), x)                          # aleteo de mamá
pon(phrase(1900, 3, .05, 21), LLEGA + 1.8)                                                   # mamá: «mi amor…»
pon(phrase(2600, 2, .045, 23), ABRAZO + .4)                                                  # bebé feliz en el abrazo
au *= np.clip(np.minimum(tt(DUR) / .3, (DUR - tt(DUR)) / .9), 0, 1)[:n]
au = lp(au, 7500, 4)
import scipy.io.wavfile as wv
wv.write(TMP / "audio_raw.wav", SR, (au / (np.max(np.abs(au)) + 1e-9) * 0.7 * 32767).astype(np.int16))
ff("-i", str(TMP / "audio_raw.wav"), "-af", "loudnorm=I=-17.2:TP=-2.5:LRA=7", "-ar", "44100", str(TMP / "audio.wav"))

final = SAL / "cap1-atrapa-la-gota-v5.mp4"
ff("-i", str(actual), "-i", str(TMP / "audio.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
   "-shortest", "-movflags", "+faststart", str(final))
r = subprocess.run([FF, "-hide_banner", "-i", str(final), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
print(r.stderr[r.stderr.rfind("Integrated loudness:"):r.stderr.rfind("Integrated loudness:") + 60].strip())
print(r.stderr[r.stderr.rfind("Peak:"):].strip()[:25])
print("LISTO", final, f"{DUR:.1f} s")
