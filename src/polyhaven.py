"""Descarga recursos CC0 de Poly Haven (https://polyhaven.com, licencia CC0: uso comercial libre, sin atribución obligatoria).
Uso: python src/polyhaven.py hdri <id> [res]   |   python src/polyhaven.py modelo <id> [res]
Guarda en assets/polyhaven/<id>/ (modelos en glTF para no abrir .blend de terceros)."""
import json, pathlib, sys, urllib.request
RAIZ = pathlib.Path(__file__).resolve().parents[1] / "assets" / "polyhaven"
UA = {"User-Agent": "pahubi-animacion-3d"}
def bajar(url, destino):
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists(): return
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA)) as r: destino.write_bytes(r.read())
tipo, ident = sys.argv[1], sys.argv[2]; res = sys.argv[3] if len(sys.argv) > 3 else ("4k" if tipo == "hdri" else "2k")
f = json.load(urllib.request.urlopen(urllib.request.Request(f"https://api.polyhaven.com/files/{ident}", headers=UA)))
d = RAIZ / ident
if tipo == "hdri":
    x = f["hdri"][res]["hdr"]; bajar(x["url"], d / f"{ident}_{res}.hdr")
else:
    x = f["gltf"][res]["gltf"]; bajar(x["url"], d / pathlib.Path(x["url"]).name)
    for rel, inc in x.get("include", {}).items(): bajar(inc["url"], d / rel)
print("ok", ident, res)
