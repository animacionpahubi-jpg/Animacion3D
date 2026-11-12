"""«¡TÚ PUEDES!» — textos (título y cierre, estilo logo Pahubi) y audio propio para el montaje en Remotion (editor/src/TuPuedes.tsx).
Tiempos = línea de tiempo final de TuPuedes.tsx (24 fps, 609 cuadros). Salida en editor/public/: cap2-titulo.png, cap2-cierre.png, cap2-audio.wav.
Texto en zona segura: entre el 15 % superior y el 25 % inferior (título al 22–28 % del alto)."""
import math, pathlib, subprocess, sys
import numpy as np
import imageio_ffmpeg, scipy.io.wavfile as wv
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RAIZ = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(RAIZ / "src"))
PUB = RAIZ / "editor" / "public"; FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1080, 1920
MORADO, RELIEVE, CREMA = (147, 62, 143), (99, 41, 131), (254, 251, 229)


def letrero(lineas, tam, y0, salida, corazon=False, cx0=None):
    f = ImageFont.truetype(str(RAIZ / "assets" / "fuentes" / "Fredoka.ttf"), tam)
    try: f.set_variation_by_axes([700, 100])
    except Exception: pass
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); PROF, BORDE = max(6, tam // 15), max(8, tam // 11)
    for i, linea in enumerate(lineas):
        d = ImageDraw.Draw(im); caja = d.textbbox((0, 0), linea, font=f, stroke_width=BORDE)
        ancho = caja[2] - caja[0] + (int(tam * .9) if corazon and i == len(lineas) - 1 else 0)
        x = (int(cx0 - ancho / 2) if cx0 else (W - ancho) // 2) - caja[0]; y = y0 + i * int(tam * 1.17)
        s = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(s).text((x + 8, y + PROF + 12), linea, font=f, fill=(40, 10, 50, 140), stroke_width=BORDE, stroke_fill=(40, 10, 50, 140))
        im = Image.alpha_composite(im, s.filter(ImageFilter.GaussianBlur(10))); d = ImageDraw.Draw(im)
        for k in range(PROF + 1): d.text((x + k * .5, y + k), linea, font=f, fill=CREMA, stroke_width=BORDE, stroke_fill=CREMA)
        for k in range(1, PROF + 1): d.text((x + k * .5, y + k), linea, font=f, fill=RELIEVE)
        d.text((x, y), linea, font=f, fill=MORADO)
        if corazon and i == len(lineas) - 1:   # corazón dibujado (la fuente no trae emojis)
            cx, cy, r = x + caja[2] + int(tam * .5), y + int(tam * .62), tam * .36
            pts = [(cx + r * 16 * math.sin(t) ** 3 / 16, cy - r * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16)
                   for t in np.linspace(0, 2 * math.pi, 120)]
            d.polygon(pts, fill=(236, 72, 120), outline=CREMA, width=6)
    im.save(salida)


letrero(["¡TÚ PUEDES!"], 135, 450, PUB / "cap2-titulo.png")                          # 22–30 % del alto
letrero(["¡Envíaselo", "a quien amas!"], 112, 292, PUB / "cap2-cierre.png", corazon=True)  # arriba, sobre el abrazo
letrero(["¡PLOF!"], 150, 900, PUB / "cap2-plof.png", cx0=800)                        # junto al bebé caído (a su derecha)
letrero(["¡Tú puedes, hijo!", "¡Vuela!"], 105, 1160, PUB / "cap2-mama-dice.png")     # mamá lo anima (0:04)
letrero(["¡YO PUEDO!"], 125, 320, PUB / "cap2-yopuedo.png")                            # arriba, sobre la cresta de mamá

# --- audio --------------------------------------------------------------------------------------------
from audio_kit import SR, piano, mbox, pluckn, fq, flapf, whoosh, phrase, dropb, lp, tt
DUR = 625 / 24
n = int(SR * DUR); au = np.zeros(n)
def pon(x, t, g=1.0):
    i = int(t * SR)
    if 0 <= i < n: x = x[: n - i]; au[i:i + len(x)] += x * g
def boing(g=.12, d=.35, f0=180, f1=520):
    t = tt(d); f = f0 + (f1 - f0) * (1 - np.exp(-t * 9)) + 40 * np.sin(2 * np.pi * 14 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * g
def mareo(g=.05, d=1.1):
    t = tt(d); f = 900 + 350 * np.sin(2 * np.pi * 3 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * g * np.minimum(1, np.minimum(t / .1, (d - t) / .4))
def zumbido(d, g=.03, f=160, sube=0):
    t = tt(d); fr = f + sube * t / d
    x = np.sign(np.sin(2 * np.pi * np.cumsum(fr) / SR)) * .5 + np.sin(2 * np.pi * np.cumsum(fr) / SR) * .5
    return lp(x, 900, 2) * g * np.minimum(1, np.minimum(t / .15, (d - t) / .25))
# momentos (s)
UY, MAMA_ENTRA, SALTO, ALETEO1, ALETEO2, CAE, PLOP = .6, 2.3, 5.8, 6.1, 6.6, 6.95, 7.3
SE_LEVANTA, MAREO, RISA, P4, YOPUEDO, DESPEGA, P5, ABRAZO, LOHICE, CIERRE = 10.4, 12.9, 13.4, 14.33, 15.6, 17.6, 19.33, 21.8, 22.3, 24.04
# música: suspenso suave → juguetona en la caída → sube al volar → tierna en el abrazo
for i, nt in enumerate(["C6", "E6", "G6"]): pon(mbox(fq(nt), 1.2, .07), .15 + i * .12)            # brillo del título
for k, nt in enumerate(["A4", "C5", "B4", "A4", "E4", "A4", "C5", "E5"]): pon(mbox(fq(nt), 1.4, .05), .4 + k * .6)
t = CAE
for nt in ["G4", "C5", "E4", "G4", "A4", "F4", "C5", "G4", "E4", "C5", "D5", "G4", "E4", "C5"]:
    if t > P4 - .3: break
    pon(pluckn(fq(nt), .45, .08), t); t += .45
t = P4 + .2
for nt in ["C5", "D5", "E5", "G5", "A5", "C6", "D6", "E6"]:                               # escala que sube mientras aprende
    pon(mbox(fq(nt), 1.0, .06), t); t += .55
t = P5
while t < DUR - 1.2:
    for ac in (["C5", "E5", "G5"], ["F4", "A4", "C5"], ["G4", "B4", "D5"], ["C5", "E5", "G5"]):
        if t > DUR - 1.2: break
        for j, nt in enumerate(ac): pon(piano(fq(nt), 2.2, .07 - j * .01), t + j * .04)
        t += 1.5
# efectos y vocecitas (sintetizadas)
pon(phrase(2600, 2, .05, 5), UY)                                              # «uy…» tembloroso
pon(zumbido(P4 + 5 - MAMA_ENTRA, .025, 150), MAMA_ENTRA)                       # alas de mamá
pon(flapf(.05), ALETEO1); pon(flapf(.05), ALETEO2)                             # flap… flap…
pon(whoosh(.5, .05, 300, 900), CAE)                                           # cae
pon(dropb(.09), PLOP); pon(boing(.07, .25, 140, 260), PLOP)                    # ¡bup!
pon(mud(.06) if False else whoosh(.35, .02, 300, 700), SE_LEVANTA)                # se levanta
pon(mareo(), MAREO)                                                          # silbidito de mareo
pon(phrase(2500, 2, .05, 7), PLOP + .45)                                    # «¡ay!»
for i in range(4): pon(phrase(2800 + 120 * i, 2, .05, 11 + i), RISA + i * .27)  # risita
pon(zumbido(P5 + 1.5 - DESPEGA, .03, 190, 140), DESPEGA)                       # sus alas cada vez más rápido
pon(phrase(2900, 3, .055, 31), YOPUEDO)                                        # «¡yo puedo!»
pon(phrase(1900, 4, .05, 41), 3.95)                                           # mamá: «¡tú puedes, hijo!»
pon(phrase(1900, 3, .05, 21), ABRAZO - .2)                                     # mamá: «¡muy bien!»
pon(phrase(2700, 3, .05, 33), LOHICE)                                          # «¡lo hice!»
pon(mbox(fq("G6"), 1.6, .06), CIERRE); pon(mbox(fq("C7"), 1.6, .05), CIERRE + .15)
au *= np.clip(np.minimum(tt(DUR) / .2, (DUR - tt(DUR)) / 1.0), 0, 1)[:n]
au = lp(au, 7500, 4)
crudo = PUB / "_cap2_raw.wav"; wv.write(crudo, SR, (au / (np.max(np.abs(au)) + 1e-9) * .7 * 32767).astype(np.int16))
subprocess.run([FF, "-v", "error", "-y", "-i", str(crudo), "-af", "loudnorm=I=-17.2:TP=-2.5:LRA=7", "-ar", "44100", str(PUB / "cap2-audio.wav")], check=True)
crudo.unlink(); print("listo", f"{DUR:.2f} s")
