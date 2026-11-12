"""Montaje de «¡Atrapa la gota!» v2 (vertical 1080x1920, 24 fps) — 4 planos Kling 3.0 Pro sobre cuadros clave de ChatGPT (Codex).
Guion: 1) con sed ve la gota en la hoja, cae y se lanza (A)  2) picada y cae al barro (B)  3) otra gota le cae en el pico y se ríe (C)
4) llega mamá, sacude la hoja y la lluvia de gotas lo deja limpio (D).
Kling entrega 2:3; cada plano se escala a 1920 de alto y se recorta a 1080 de ancho con su desplazamiento X.
Título con el estilo del logo Pahubi. Audio sintetizado propio (src/audio_kit.py), normalizado a −18 LUFS / pico ≤ −2,5 dBTP.
Uso: python src/montaje_cap1v2.py  → capitulos/cap1-atrapa-la-gota/cap1-atrapa-la-gota-v2.mp4"""
import pathlib, subprocess, sys
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
FF = imageio_ffmpeg.get_ffmpeg_exe()
IA = RAIZ / "pruebas" / "ia"
SAL = RAIZ / "capitulos" / "cap1-atrapa-la-gota"; SAL.mkdir(parents=True, exist_ok=True)
TMP = SAL / "tmp2"; TMP.mkdir(exist_ok=True)
FPS, W, H = 24, 1080, 1920
# (archivo, desde, hasta, desplazamiento X del recorte en el ancho escalado de 1280; None = centrado)
PLANOS = [("cap1v2-A-salto", 0.0, 4.1, None), ("cap1v2-B-barro", 1.5, 5.0, None),
          ("cap1v2-C-risa", 0.0, 4.4, None), ("cap1v2-D-ducha", 0.0, 4.4, 40)]
ABRAZO = RAIZ / "personajes" / "generadas" / "cap1-k7-abrazo.png"   # final: imagen fija con acercamiento lento (gratis)
T_ABR, T_XF = 3.8, 0.7                                                 # duración del abrazo y del fundido hacia él
DUR = sum(b - a for _, a, b, _ in PLANOS) + T_ABR - 2 * T_XF            # fundidos: risa→mamá y lluvia→abrazo
INI = np.cumsum([0] + [b - a for _, a, b, _ in PLANOS]); INI[3:] -= T_XF; INI[4:] -= T_XF   # inicio de cada plano (con los fundidos)
# momentos de sonido, en segundos DENTRO de cada plano (medidos en los clips)
EV = {"suelta": (0, 2.8), "salto": (0, 3.4), "chapuzon": (1, 1.25), "gota_pico": (2, 2.7), "llega_mama": (3, 0.2), "toque_hoja": (3, 2.3)}


def ff(*a): subprocess.run([FF, "-v", "error", "-y", *a], check=True)


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

# --- planos ---------------------------------------------------------------------------------------------
lista = []
for i, (nom, a, b, dx) in enumerate(PLANOS):
    sw = round(H * 2 / 3 / 2) * 2                                      # ancho al escalar 2:3 a 1920 de alto (1280)
    cx = (sw - W) // 2 if dx is None else dx
    v = f"[0]scale={sw}:{H},crop={W}:{H}:{cx}:0,fps={FPS},setpts=PTS-STARTPTS"
    if i == 0:
        args = ["-ss", str(a), "-t", str(b - a), "-i", str(IA / f"{nom}.mp4"), "-loop", "1", "-i", str(TMP / "titulo.png"), "-filter_complex",
                v + "[v];[1]format=rgba,fade=t=in:st=0.2:d=0.35:alpha=1,fade=t=out:st=2.3:d=0.4:alpha=1[t];"
                "[v][t]overlay=0:'-40*exp(-8*t)*cos(14*t)':shortest=1,format=yuv420p[o]", "-map", "[o]"]
    else:
        args = ["-ss", str(a), "-t", str(b - a), "-i", str(IA / f"{nom}.mp4"), "-filter_complex", v + ",format=yuv420p[o]", "-map", "[o]"]
    ff(*args, "-an", "-c:v", "libx264", "-crf", "16", str(TMP / f"p{i}.mp4")); lista.append(TMP / f"p{i}.mp4")
# abrazo: acercamiento lento sobre la imagen fija, fundido desde la lluvia y fundido a negro al final
NF = int(T_ABR * FPS)
ff("-loop", "1", "-i", str(ABRAZO), "-filter_complex",
   f"[0]scale=2560:3840,zoompan=z='1+0.07*on/{NF}':x='iw/2-(iw/zoom/2)':y='ih*0.45-(ih/zoom*0.45)':d={NF}:s=1280x1920:fps={FPS},"
   f"crop={W}:{H}:100:0,fade=t=out:st={T_ABR - 0.8}:d=0.8,format=yuv420p[o]", "-map", "[o]", "-frames:v", str(NF),
   "-c:v", "libx264", "-crf", "16", str(TMP / "abrazo.mp4"))
ultimo = lista.pop(); dur_ult = PLANOS[-1][2] - PLANOS[-1][1]
ff("-i", str(ultimo), "-i", str(TMP / "abrazo.mp4"), "-filter_complex",
   f"[0][1]xfade=transition=fade:duration={T_XF}:offset={dur_ult - T_XF},format=yuv420p[o]", "-map", "[o]",
   "-c:v", "libx264", "-crf", "16", str(TMP / "fin.mp4"))
risa = lista.pop(); dur_risa = PLANOS[2][2] - PLANOS[2][1]                  # fundido risa → llegada de mamá
ff("-i", str(risa), "-i", str(TMP / "fin.mp4"), "-filter_complex",
   f"[0][1]xfade=transition=fade:duration={T_XF}:offset={dur_risa - T_XF},format=yuv420p[o]", "-map", "[o]",
   "-c:v", "libx264", "-crf", "16", str(TMP / "fin2.mp4"))
lista.append(TMP / "fin2.mp4")
(TMP / "lista.txt").write_text("".join(f"file '{p.as_posix()}'\n" for p in lista), encoding="utf-8")
ff("-f", "concat", "-safe", "0", "-i", str(TMP / "lista.txt"), "-c", "copy", str(TMP / "video.mp4"))

# --- audio ----------------------------------------------------------------------------------------------
from audio_kit import SR, piano, mbox, pluckn, fq, flapf, whoosh, mud, phrase, dropb, lp, tt
n = int(SR * DUR); au = np.zeros(n)
def pon(x, t, g=1.0):
    i = int(t * SR)
    if 0 <= i < n: x = x[: n - i]; au[i:i + len(x)] += x * g
def T(e): p, s = EV[e]; return INI[p] + s
# música: curiosa hasta el chapuzón, juguetona en la risa, tierna con mamá
t = .1
for nota in ["E5", "G5", "A5", "C6", "A5", "G5", "E5", "G5", "A5", "C6", "D6", "C6", "A5", "G5", "E5"]:
    if t > T("chapuzon") - .3: break
    pon(mbox(fq(nota), 1.2, .075), t); t += .62
t = T("chapuzon") + .5
for nota in ["C4", "G4", "E4", "G4", "D4", "A4", "F4", "A4", "C5", "G4", "E4", "G4"]:
    if t > INI[3] - .2: break
    pon(pluckn(fq(nota), .45, .08), t); t += .5
t = INI[3] + .1
for acorde in (["C5", "E5", "G5"], ["F4", "A4", "C5"], ["G4", "B4", "D5"], ["F4", "A4", "C5"], ["C5", "E5", "G5"]):
    for j, nota in enumerate(acorde): pon(piano(fq(nota), 2.0, .07 - j * .01), t + j * .04)
    t += 1.5
# efectos
for i, nt in enumerate(["C6", "E6", "G6"]): pon(mbox(fq(nt), 1.2, .07), .25 + i * .12)            # brillo del título
pon(phrase(2700, 2, .04, 3), 1.3)                                                                    # «mmm» con sed
pon(dropb(.05), T("suelta"))                                                                         # la gota se suelta
for x in np.arange(T("salto"), INI[1] + 1.1, 1 / 12): pon(flapf(.045), x)                           # aleteo
pon(whoosh(1.0, .07, 300, 1500), INI[1])                                                       # picada
pon(mud(.28), T("chapuzon"))                                                                          # ¡splash!
pon(phrase(2500, 2, .05, 5), T("chapuzon") + .6)                                                     # «¿eh?»
pon(dropb(.06), T("gota_pico"))                                                                       # ¡plip! en el pico
for i in range(4): pon(phrase(2800 + 120 * i, 2, .05, 11 + i), T("gota_pico") + .3 + i * .28)     # risita
for x in np.arange(T("llega_mama"), T("llega_mama") + 1.2, 1 / 10): pon(flapf(.03), x)              # aleteo de mamá
pon(whoosh(.5, .03, 800, 2500), T("toque_hoja"))                                                     # toque a la hoja
rng = np.random.default_rng(7)
for x in T("toque_hoja") + .2 + np.sort(rng.uniform(0, 2.6, 22)): pon(dropb(.018 + .012 * rng.random()), x)   # lluvia de gotas
for i in range(3): pon(phrase(3000 + 150 * i, 2, .045, 21 + i), T("toque_hoja") + 1.6 + i * .3)    # risa final
T_A = INI[4]                                                                                  # empieza el abrazo
pon(phrase(2200, 2, .045, 31), T_A + .4); pon(phrase(2900, 2, .04, 32), T_A + .7)                  # «awww» de los dos
for i, nt in enumerate(["G5", "C6", "E6"]): pon(mbox(fq(nt), 1.6, .06), T_A + 1.2 + i * .18)     # brillito final
au *= np.clip(np.minimum(tt(DUR) / .3, (DUR - tt(DUR)) / .9), 0, 1)[:n]
au = lp(au, 7500, 4)
import scipy.io.wavfile as wv
wv.write(TMP / "audio_raw.wav", SR, (au / (np.max(np.abs(au)) + 1e-9) * 0.7 * 32767).astype(np.int16))
ff("-i", str(TMP / "audio_raw.wav"), "-af", "loudnorm=I=-17.6:TP=-2.5:LRA=7", "-ar", "44100", str(TMP / "audio.wav"))

final = SAL / "cap1-atrapa-la-gota-v2.mp4"
ff("-i", str(TMP / "video.mp4"), "-i", str(TMP / "audio.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
   "-shortest", "-movflags", "+faststart", str(final))
r = subprocess.run([FF, "-hide_banner", "-i", str(final), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
print(r.stderr[r.stderr.rfind("Integrated loudness:"):r.stderr.rfind("Integrated loudness:") + 60].strip())
print(r.stderr[r.stderr.rfind("Peak:"):].strip()[:25])
print("LISTO", final, f"{DUR:.1f} s")
