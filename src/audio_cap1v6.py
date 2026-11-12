"""Audio de «¡Atrapa la gota!» v6 (montaje en Remotion: editor/src/AtrapaLaGota.tsx). Mismos sonidos que v5, sincronizados con la
línea de tiempo de Remotion (24 fps, 596 cuadros). Salida: editor/public/audio.wav a −18 LUFS, pico ≤ −2,5 dBTP.
Si cambias la duración de un tramo en el .tsx, actualiza aquí los tiempos (segundos de la línea de tiempo final)."""
import pathlib, subprocess, sys
import numpy as np
import imageio_ffmpeg, scipy.io.wavfile as wv

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from audio_kit import SR, piano, mbox, pluckn, fq, flapf, whoosh, mud, phrase, dropb, lp, tt
FF = imageio_ffmpeg.get_ffmpeg_exe()
DUR = 596 / 24
SUELTA, SALTO, CHAPUZON = 1.1, 1.6, 3.5               # plano A (empieza en 0)
PLIP, LLEGA = 9.29, 10.23                             # plano B (gota en el pico, llega mamá)
ABRAZO = 19.13                                        # plano C

n = int(SR * DUR); au = np.zeros(n)
def pon(x, t, g=1.0):
    i = int(t * SR)
    if 0 <= i < n: x = x[: n - i]; au[i:i + len(x)] += x * g
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
for i, nt in enumerate(["C6", "E6", "G6"]): pon(mbox(fq(nt), 1.2, .07), .2 + i * .12)      # brillo del título
pon(phrase(2700, 2, .04, 3), .5)                                                             # «mmm» con sed
pon(dropb(.05), SUELTA)
for x in np.arange(SALTO, CHAPUZON - .2, 1 / 12): pon(flapf(.04), x)
pon(whoosh(1.2, .07, 300, 1500), SALTO + .3)
pon(mud(.28), CHAPUZON)
pon(phrase(2500, 2, .05, 5), CHAPUZON + .7)
pon(dropb(.06), PLIP)
for i in range(5): pon(phrase(2800 + 120 * i, 2, .05, 11 + i), PLIP + .3 + i * .26)
for x in np.arange(LLEGA, LLEGA + 1.6, 1 / 10): pon(flapf(.03), x)
pon(phrase(1900, 3, .05, 21), LLEGA + 1.8)
pon(phrase(2600, 2, .045, 23), ABRAZO + .4)
au *= np.clip(np.minimum(tt(DUR) / .3, (DUR - tt(DUR)) / .9), 0, 1)[:n]
au = lp(au, 7500, 4)
TMP = RAIZ / "editor" / "public"; crudo = TMP / "_audio_raw.wav"
wv.write(crudo, SR, (au / (np.max(np.abs(au)) + 1e-9) * 0.7 * 32767).astype(np.int16))
subprocess.run([FF, "-v", "error", "-y", "-i", str(crudo), "-af", "loudnorm=I=-17.2:TP=-2.5:LRA=7", "-ar", "44100", str(TMP / "audio.wav")], check=True)
crudo.unlink(); print("audio.wav", f"{DUR:.2f} s")
