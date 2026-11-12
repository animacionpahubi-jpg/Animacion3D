> **DISEÑO OFICIAL VIGENTE (desde 2026-11-10): `personajes/personajes_finales/`** — bebé: bebe-pose.jpg, bebe-expresiones.jpg (gorro magenta con rayas rosadas, pompón atrás, 3 hojitas que salen POR ENCIMA del gorro, pico azul marino largo); mamá: mama-vistas.jpg, mama-pose.jpg, mama-expresiones.jpg (sin gorro, cresta suave peinada hacia atrás, pestañas largas). Las fichas de abajo y `personajes/hojas/` son el diseño anterior: NO usarlas como referencia.

# Fichas oficiales de personajes — Pahubi Animación 3D (Fase 0)

Estilo de todos: 3D tipo película animada, textura de peluche suave (plumón fino), ojos grandes brillantes, cachetes rosados, luz cálida.
Referencias en `referencias/` (hojas de expresiones de ChatGPT y el pollito del 2D). Las hojas finales van en `hojas/`.

## Colibrí bebé (protagonista)
| Rasgo | Decisión |
|---|---|
| Cuerpo | Redondito, verde lima; panza amarillo crema |
| Gorro | Tejido morado con franjas lila horizontales y pompón morado esponjoso; siempre puesto (salvo historias que pidan quitárselo) |
| Cresta | 2–3 plumitas verdes en forma de hoja que salen por encima del gorro |
| Ojos | Grandes, iris morado oscuro, dos brillos blancos; cejas finas verde oscuro; SIN pestañas |
| Pico | Azul pizarra, recto y fino. **Largo oficial = el de `hojas/bebe-hoja-original.png`** (≈ 0,6 × el ancho de la cabeza), igual en todas las tomas |
| Boca | Se abre solo en la base del pico (lengua rosada) |
| Alas | Rosadas con puntas lila suave |
| Cola | 3 plumas rosadas |
| Patas | Moradas, cortas, 3 deditos redondeados |
| Tamaño | ≈ 60 % de la altura de mamá |

## Mamá colibrí
| Rasgo | Decisión |
|---|---|
| Cuerpo | Verde lima como el bebé, más alta y estilizada; panza amarillo crema |
| Cabeza | SIN gorro; penacho de plumas verdes en abanico |
| Ojos | Iris morado, dos brillos, **pestañas negras** (la distingue del bebé) |
| Pico | Azul pizarra, recto y fino, más largo que el del bebé (≈ 0,9 × el ancho de la cabeza; ver `hojas/mama-hoja-original.png`) |
| Alas | Rosadas con degradé lila/morado hacia la base |
| Patas | Moradas, 3 deditos |

## Pollito (amigo)
| Rasgo | Decisión |
|---|---|
| Cuerpo | Bolita esponjosa color arena/caramelo claro; pecho más claro |
| Cabeza | Plumón despeinado arriba, sin cresta ni gorro |
| Ojos | Negros grandes con brillo blanco, cejas cafés, cachetes rosados |
| Pico | Corto, triangular, naranja |
| Alas | Cafés claras con plumas marcadas; colita de 3–4 plumas |
| Patas | Naranja-café, delgadas, 3 dedos |
| Tamaño | ≈ igual que el colibrí bebé |

## Estado de las hojas (2026-11-07)
| Personaje | Hoja | Estado |
|---|---|---|
| Colibrí bebé | `hojas/bebe-hoja.png` (1672×941) | ✅ Oficial |
| Mamá colibrí | `hojas/mama-hoja.png` (1088×608, GPT Image 2.6 en fal.ai) | ✅ Oficial |
| Pollito | `hojas/pollito-hoja.png` (1088×608, GPT Image 2.6 en fal.ai) | ✅ Oficial |
Para generar más imágenes con el modelo de ChatGPT: `python src/fal_imagen.py NOMBRE "prompt" ref1,ref2` (gasto del 3D en `config/fal_gasto.json`, tope 10 USD).
Las `*-hoja.png` tienen la cara del cuerpo entero tapada con gris (`src/hojas_personaje.py`); las `*-original.png` son las de ChatGPT sin tocar.

## Formato de hoja de personaje (video 2)
- Lienzo **16:9** horizontal, fondo **gris neutro liso** (#808080), sin texto.
- **3 secciones iguales**: (1) primer plano de la cara de frente en alta resolución, (2) cuerpo entero de frente, (3) cuerpo entero de espaldas.
- Después: **borrar la cara** de las secciones 2 y 3 (tapar con gris) → archivo `hojas/<personaje>-hoja.png`; se guarda también la original `hojas/<personaje>-hoja-original.png`.

## Textos para ChatGPT
Adjuntar SIEMPRE la hoja de expresiones del personaje (o la imagen 2D del pollito) junto al texto.

**Colibrí bebé**
```
Usando EXACTAMENTE este personaje (adjunto su hoja de expresiones), crea una hoja de personaje horizontal 16:9 con fondo gris neutro liso (#808080, no blanco), dividida en solo 3 secciones iguales: 1) primer plano de la cara de frente, en alta resolución, expresión alegre neutra; 2) cuerpo entero de frente; 3) cuerpo entero de espaldas. Estilo 3D de película animada con textura de peluche suave. Rasgos fijos: cuerpo verde lima redondito con panza amarillo crema; gorro tejido morado con franjas lila horizontales y pompón morado; 2-3 plumitas verdes en forma de hoja asomando sobre el gorro; ojos grandes con iris morado oscuro y dos brillos, sin pestañas; pico azul pizarra recto y fino de largo igual a 0,9 veces el ancho de la cabeza; alas rosadas con puntas lila; cola de 3 plumas rosadas; patas moradas cortas con 3 deditos. Luz suave de estudio, sin sombras duras, sin texto ni objetos extra.
```

**Mamá colibrí**
```
Usando EXACTAMENTE este personaje (adjunto su hoja de expresiones), crea una hoja de personaje horizontal 16:9 con fondo gris neutro liso (#808080, no blanco), dividida en solo 3 secciones iguales: 1) primer plano de la cara de frente, en alta resolución, expresión tierna; 2) cuerpo entero de frente; 3) cuerpo entero de espaldas. Estilo 3D de película animada con textura de peluche suave. Rasgos fijos: colibrí adulta verde lima, más alta y estilizada que un pichón, panza amarillo crema; sin gorro; penacho de plumas verdes en abanico; ojos grandes con iris morado, dos brillos y pestañas negras; pico azul pizarra recto y fino de largo igual a 1,1 veces el ancho de la cabeza; alas rosadas con degradé lila hacia la base; patas moradas con 3 dedos. Luz suave de estudio, sin sombras duras, sin texto ni objetos extra.
```

**Pollito** (primero pasarlo al estilo 3D)
```
Convierte este pollito (adjunto mi dibujo 2D) al mismo estilo 3D de película animada con textura de peluche suave que mis colibríes (adjunto la hoja del colibrí bebé como referencia de estilo), y crea su hoja de personaje horizontal 16:9 con fondo gris neutro liso (#808080, no blanco), dividida en solo 3 secciones iguales: 1) primer plano de la cara de frente, en alta resolución, expresión alegre; 2) cuerpo entero de frente; 3) cuerpo entero de espaldas. Rasgos fijos: bolita esponjosa color arena caramelo claro con el pecho más claro; plumón despeinado arriba de la cabeza, sin cresta; ojos negros grandes con brillo blanco, cejas cafés y cachetes rosados; pico corto triangular naranja; alas cafés claras con plumas marcadas y colita de 3-4 plumas; patas delgadas naranja-café con 3 dedos; del mismo tamaño que el colibrí bebé. Luz suave de estudio, sin sombras duras, sin texto ni objetos extra.
```
