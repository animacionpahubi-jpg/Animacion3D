"""«¡TÚ PUEDES!» CON VOCES (Kling audio nativo en español): subtítulos + audio para editor/src/TuPuedesVoces.tsx (24 fps, 632 cuadros).
Voces: se toman de los clips de Kling SOLO en la ventana donde hablan (sin la música ni ruidos raros del clip) y la música propia
baja (ducking) mientras suenan. Salida en editor/public/: cap2v-sub-*.png, cap2v-audio.wav (−18 LUFS tras el 0,62 del montaje)."""
import pathlib, subprocess, sys
import numpy as np
import imageio_ffmpeg, scipy.io.wavfile as wv

RAIZ = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(RAIZ / "src"))
PUB = RAIZ / "editor" / "public"; IA = RAIZ / "pruebas" / "ia"; FF = imageio_ffmpeg.get_ffmpeg_exe()
sys.argv = [sys.argv[0]]
import importlib.util
spec = importlib.util.spec_from_file_location("t", RAIZ / "src" / "cap2_textos_audio.py")   # reusa letrero() (y regenera los letreros base)
t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
letrero = t.letrero
letrero(["«¡Mami, mira!", "¡Estoy volando!»"], 72, 300, PUB / "cap2v-sub-mira.png")
letrero(["«¡Lo lograste, mi amor!»"], 72, 300, PUB / "cap2v-sub-lograste.png")
letrero(["«¡Te quiero, mami!»"], 72, 300, PUB / "cap2v-sub-tequiero.png")
letrero(["«¡Tú puedes, hijo!", "¡Vuela!»"], 80, 1180, PUB / "cap2-mama-dice.png")

from audio_kit import SR, piano, mbox, pluckn, fq, flapf, whoosh, dropb, lp, tt
DUR = 632 / 24; n = int(SR * DUR); au = np.zeros(n)
def pon(x, t0, g=1.0, buf=None):
    b = au if buf is None else buf; i = int(t0 * SR)
    if 0 <= i < n: x = x[: n - i]; b[i:i + len(x)] += x * g
def zumbido(d, g=.03, f=160, sube=0):
    tt_ = tt(d); fr = f + sube * tt_ / d
    x = np.sign(np.sin(2 * np.pi * np.cumsum(fr) / SR)) * .5 + np.sin(2 * np.pi * np.cumsum(fr) / SR) * .5
    return lp(x, 900, 2) * g * np.minimum(1, np.minimum(tt_ / .15, (d - tt_) / .25))
def mareo(g=.05, d=1.1):
    tt_ = tt(d); f = 900 + 350 * np.sin(2 * np.pi * 3 * tt_)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * g * np.minimum(1, np.minimum(tt_ / .1, (d - tt_) / .4))
# línea de tiempo (s)
P2, P3, P4, P5, CIERRE = 5.0, 9.33, 14.33, 19.33, 24.33
CAE, PLOP, MAREO, DESPEGA = 6.95, 7.3, 12.9, P4 + 2.0
# voces: (clip, desde, hasta, inicio en la línea de tiempo)
VOCES = [("cap3-voz-prueba", 1.8, 5.03, 1.8), ("cap2v-P4", 1.8, 5.03, P4 + 1.8), ("cap2v-P5", 1.4, 5.03, P5 + 1.4)]   # hasta el FINAL del clip: las frases terminan cerca de los 4,7–5,0 s
voz = np.zeros(n)
for clip, a, b, t0 in VOCES:
    w = IA / f"{clip}-voz.wav"
    subprocess.run([FF, "-v", "error", "-y", "-ss", str(a), "-t", str(b - a), "-i", str(IA / f"{clip}.mp4"), "-vn", "-ac", "1", "-ar", str(SR),
                    "-af", "highpass=f=180,loudnorm=I=-18:TP=-3", str(w)], check=True)
    _, x = wv.read(w); x = x.astype(float) / 32768; m = int(.03 * SR)
    x[:m] *= np.linspace(0, 1, m); x[-m:] *= np.linspace(1, 0, m); pon(x, t0, buf=voz)
# música
for i, nt in enumerate(["C6", "E6", "G6"]): pon(mbox(fq(nt), 1.2, .07), .15 + i * .12)
for k, nt in enumerate(["A4", "C5", "B4", "A4", "E4", "A4", "C5", "E5"]): pon(mbox(fq(nt), 1.4, .05), .4 + k * .6)
tm = CAE
for nt in ["G4", "C5", "E4", "G4", "A4", "F4", "C5", "G4", "E4", "C5", "D5", "G4", "E4", "C5", "G4"]:
    if tm > P4 - .3: break
    pon(pluckn(fq(nt), .45, .08), tm); tm += .45
tm = P4 + .2
for nt in ["C5", "D5", "E5", "G5", "A5", "C6", "D6", "E6"]: pon(mbox(fq(nt), 1.0, .06), tm); tm += .6
tm = P5
while tm < DUR - 1.2:
    for ac in (["C5", "E5", "G5"], ["F4", "A4", "C5"], ["G4", "B4", "D5"], ["C5", "E5", "G5"]):
        if tm > DUR - 1.2: break
        for j, nt in enumerate(ac): pon(piano(fq(nt), 2.2, .07 - j * .01), tm + j * .04)
        tm += 1.5
# efectos
pon(zumbido(P2 - 2.3, .025, 150), 2.3); pon(zumbido(P5 + 1.0 - P4, .025, 150), P4)       # alas de mamá
pon(flapf(.05), 6.1); pon(flapf(.05), 6.6); pon(whoosh(.5, .05, 300, 900), CAE)
pon(dropb(.09), PLOP); pon(t.boing(.07, .25, 140, 260), PLOP)                               # ¡PUM!
pon(mareo(), MAREO)
pon(zumbido(P5 - DESPEGA, .03, 190, 140), DESPEGA)                                           # sus alas
pon(mbox(fq("G6"), 1.6, .06), CIERRE); pon(mbox(fq("C7"), 1.6, .05), CIERRE + .15)
# ducking: la música y efectos bajan al 35 % donde hay voz
env = np.abs(voz); from scipy.ndimage import maximum_filter1d, uniform_filter1d
hay = uniform_filter1d(maximum_filter1d((env > .02).astype(float), int(.25 * SR)), int(.15 * SR))
au *= 1 - .65 * np.clip(hay, 0, 1)
au = au / (np.max(np.abs(au)) + 1e-9) * .45 + voz / (np.max(np.abs(voz)) + 1e-9) * .75
au *= np.clip(np.minimum(tt(DUR) / .2, (DUR - tt(DUR)) / 1.0), 0, 1)[:n]
crudo = PUB / "_cap2v_raw.wav"; wv.write(crudo, SR, (au / (np.max(np.abs(au)) + 1e-9) * .8 * 32767).astype(np.int16))
subprocess.run([FF, "-v", "error", "-y", "-i", str(crudo), "-af", "loudnorm=I=-17.2:TP=-2.5:LRA=9", "-ar", "44100", str(PUB / "cap2v-audio.wav")], check=True)
crudo.unlink(); print("listo", f"{DUR:.2f} s")
