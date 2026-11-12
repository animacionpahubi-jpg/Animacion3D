"""Fase 0.3: hojas de personaje para la IA de video (formato «video 2»): se tapa con gris la cara del cuerpo entero
para que el modelo tome la cara solo del primer plano. Uso: python src/hojas_personaje.py"""
import pathlib
from PIL import Image, ImageDraw, ImageFilter
H = pathlib.Path(__file__).resolve().parents[1] / "personajes" / "hojas"

def tapar(im, caja, margen=6):
    """Óvalo gris del color del fondo cercano, con borde suavizado."""
    x0, y0, x1, y1 = caja
    fondo = im.getpixel((max(0, x0 - 40), max(0, y0 - 40)))
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).ellipse((x0 - margen, y0 - margen, x1 + margen, y1 + margen), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(3))
    im.paste(Image.new("RGB", im.size, fondo), (0, 0), m)
    return im

# colibrí bebé: hoja propia 16:9 (cara del cuerpo entero de frente)
b = Image.open(H / "bebe-hoja-original.png").convert("RGB")
tapar(b, (700, 328, 1044, 576)).save(H / "bebe-hoja.png")

# mamá y pollito: hojas propias generadas con GPT Image 2.6 en fal.ai (src/fal_imagen.py), 1088x608
G = H.parent / "generadas"
for nombre, caja in (("mama", (398, 132, 618, 258)), ("pollito", (438, 178, 662, 322))):
    im = Image.open(G / f"{nombre}-hoja-v1.png").convert("RGB"); im.save(H / f"{nombre}-hoja-original.png")
    tapar(im, caja)
    if nombre == "mama": tapar(im, (398, 222, 440, 248), margen=4)   # punta del pico, que sale del óvalo
    im.save(H / f"{nombre}-hoja.png")
print("ok")
