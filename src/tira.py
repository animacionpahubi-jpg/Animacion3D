"""Hoja de cuadros de un video para revisarlo de un vistazo (reemplaza a tira.sh; funciona en Windows, Linux y macOS).
Uso: python src/tira.py VIDEO|NOMBRE SALIDA.png [--fps 5] [--columnas 5] [--filas 5] [--ancho 230]
NOMBRE sin ruta ni extensión se busca en pruebas/ia/NOMBRE.mp4. Usa el ffmpeg de imageio-ffmpeg."""
import argparse, pathlib, subprocess, sys

import imageio_ffmpeg

RAIZ = pathlib.Path(__file__).resolve().parents[1]


def tira(video, salida, fps=5, columnas=5, filas=5, ancho=230):
    v = pathlib.Path(video)
    if not v.suffix and not v.exists():
        v = RAIZ / "pruebas" / "ia" / f"{video}.mp4"
    if not v.exists():
        sys.exit(f"No existe el video: {v}")
    pathlib.Path(salida).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y", "-i", str(v),
                    "-vf", f"fps={fps},scale={ancho}:-1,tile={columnas}x{filas}", "-frames:v", "1", str(salida)], check=True)
    return pathlib.Path(salida)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("video"); p.add_argument("salida")
    p.add_argument("--fps", type=float, default=5); p.add_argument("--columnas", type=int, default=5)
    p.add_argument("--filas", type=int, default=5); p.add_argument("--ancho", type=int, default=230)
    a = p.parse_args()
    print("ok", tira(a.video, a.salida, a.fps, a.columnas, a.filas, a.ancho))
