"""Comprueba que este PC puede producir capítulos 3D. Nunca imprime el valor de una clave.
Uso: python src/verificar_entorno.py      (sale con código 1 si falta algo obligatorio)"""
import importlib, pathlib, re, shutil, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
ENV_2D = RAIZ.parent / "ANIMACION-2D" / ".env"   # algunos scripts toman prestadas claves del 2D (solo lectura)
fallos = avisos = 0


def linea(estado, que, detalle=""):
    global fallos, avisos
    fallos += estado == "FALTA"; avisos += estado == "AVISO"
    print(f"[{estado:5}] {que}" + (f" - {detalle}" if detalle else ""))


def claves(f):
    if not f.exists(): return set()
    return {m.group(1) for l in f.read_text(encoding="utf-8").splitlines()
            if (m := re.match(r"\s*([A-Z0-9_]+)\s*=\s*\S", l)) and not l.lstrip().startswith("#")}


def version(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return (r.stdout.strip() or r.stderr.strip()).splitlines()[0]
    except Exception: return None


# 1. Python y paquetes
v = sys.version_info
linea("OK" if v >= (3, 10) else "FALTA", f"Python {v.major}.{v.minor}", sys.executable)
for paquete, modulo in (("numpy", "numpy"), ("scipy", "scipy"), ("pillow", "PIL"), ("imageio-ffmpeg", "imageio_ffmpeg")):
    try: importlib.import_module(modulo); linea("OK", f"paquete {paquete}")
    except ImportError: linea("FALTA", f"paquete {paquete}", "pip install -r requirements.txt (o ../requirements.txt)")

# 2. ffmpeg
try:
    import imageio_ffmpeg
    linea("OK", "ffmpeg", version([imageio_ffmpeg.get_ffmpeg_exe(), "-version"]) or "")
except Exception as e:
    linea("FALTA", "ffmpeg", "viene con imageio-ffmpeg")

# 3. Node y Remotion
node = shutil.which("node")
nv = version([node, "--version"]) if node else None
ok_node = bool(nv) and tuple(map(int, nv.lstrip("v").split(".")[:2])) >= (20, 19)
linea("OK" if ok_node else "FALTA", "Node >= 20.19", nv or "instalar Node 24 LTS")
remotion = (RAIZ / "editor" / "node_modules" / "remotion").exists()
linea("OK" if remotion else "FALTA", "Remotion (editor/node_modules)", "" if remotion else "cd editor && npm i")

# 4. Codex CLI (imágenes clave)
import os
APP = pathlib.Path.home() / ".codex" / "plugins" / ".plugin-appserver" / ("codex.exe" if os.name == "nt" else "codex")  # app de escritorio
codex = os.environ.get("CODEX_BIN") or shutil.which("codex.cmd") or shutil.which("codex") or (str(APP) if APP.exists() else None)
if not codex:
    linea("FALTA", "Codex CLI", "instalar la app de Codex o 'npm i -g @openai/codex' y luego 'codex login' con la cuenta ChatGPT de la empresa")
else:
    linea("OK", "Codex CLI", f"{version([codex, '--version']) or ''} ({codex})")
    sesion = version([codex, "login", "status"]) or ""
    linea("OK" if "ChatGPT" in sesion else "AVISO", "Sesión de Codex", sesion or "sin sesión: 'codex login'")
    if not (shutil.which("codex.cmd") or shutil.which("codex")):
        linea("AVISO", "codex.cmd no está en el PATH", "los claves.py actuales lo llaman así; usar CODEX_BIN o la interfaz de #18")

# 5. Claves (solo se dice si están, nunca su valor)
propias, del_2d = claves(RAIZ / ".env"), claves(ENV_2D)
if not (RAIZ / ".env").exists():
    linea("FALTA", ".env del 3D", "crear Animacion3D/.env (ver docs/CONTEXTO-3D.md)")
linea("OK" if "KLING_API_KEY" in propias else "FALTA", "KLING_API_KEY (video, de pago)", "en .env del 3D")
for k, uso in (("GEMINI_API_KEY", "transcribir voces"), ("CLOUDFLARE_ACCOUNT_ID", "FLUX gratis (prueba)"),
               ("CLOUDFLARE_API_TOKEN", "FLUX gratis (prueba)")):
    if k in propias: linea("OK", k, uso)
    elif k in del_2d: linea("AVISO", k, f"{uso}: se toma prestada de ANIMACION-2D/.env; mejor copiarla al .env del 3D")
    else: linea("AVISO", k, f"{uso}: no está en el .env del 3D ni en ANIMACION-2D/.env")
if not ENV_2D.exists() and (RAIZ.parent / "ANIMACION-2D" / "env").exists():
    linea("AVISO", "ANIMACION-2D/env sin punto", "los scripts buscan ANIMACION-2D/.env: las claves prestadas no se encuentran")

if not fallos: resumen = "Listo para producir"
elif fallos == 1: resumen = "Falta 1 requisito obligatorio"
else: resumen = f"Faltan {fallos} requisitos obligatorios"
print("\n" + resumen + (f" ({avisos} avisos)" if avisos else ""))
sys.exit(1 if fallos else 0)
