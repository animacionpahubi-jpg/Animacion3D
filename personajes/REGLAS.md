# Reglas oficiales de diseño de los personajes 3D (decididas el 2026-11-13)

Esta es la **única fuente de verdad** para generar y revisar imágenes y video del 3D: Codex (imágenes clave), Kling (video), revisión estricta y
auditorías. Si otro archivo dice algo distinto (`FICHAS.md`, prompts viejos), manda este. Las imágenes de `personajes_finales/` son la
referencia de estilo, colores y cara; donde una imagen oficial no cumpla una regla de aquí, **manda la regla** (ver «Conflictos conocidos»).

## Colibrí bebé
| Rasgo | Regla |
|---|---|
| **Copete** | **Exactamente 3 hojitas verdes, CORTAS** (no más altas que ~1/3 del alto del gorro). **Nacen de la FRENTE**: asoman por DEBAJO del borde delantero del gorro, al centro, y suben por delante de él. **Nunca** salen del tejido, nunca encima del gorro, nunca a un lado. |
| Gorro | Tejido magenta con rayas rosadas horizontales, pompón magenta esponjoso ATRÁS; siempre puesto y del mismo color. |
| Pico | Azul marino, largo, fino y recto; se ve largo y en diagonal en vista de tres cuartos; nunca curvo, corto ni cambia de largo. |
| Cuerpo y cara | Verde vivo de peluche, panza amarillo suave, ojos magenta grandes con brillos, cachetes rosados, sin pestañas. |
| Alas / patas | Alas durazno-rosado; patas moradas. |

## Mamá colibrí
| Rasgo | Regla |
|---|---|
| **Tamaño** | **≈ 1,4 × la altura del bebé**, siempre claramente más grande que él en el mismo plano. |
| **Cresta** | **5–6 plumitas en forma de hoja, mate, separadas, con puntas claras, peinadas hacia atrás.** Nunca casco liso ni pelo pegado, nunca púas, nunca penacho en abanico. |
| Gorro | Ninguno. |
| Cara | Pestañas largas (la distingue del bebé). |
| Alas / pico | Alas durazno-rosado con degradé a lila; pico azul marino largo, fino y recto, más largo que el del bebé. |

## Juntos
- En abrazos, el pico de mamá apunta hacia arriba y afuera, por encima de la cabeza del bebé: nunca toca su cara, gorro o cuerpo; los picos nunca se cruzan.

## Conflictos conocidos
- `personajes_finales/bebe-pose.jpg` muestra las hojitas saliendo por encima del gorro. Para el copete **no se usa como referencia**: el
  prompt debe decir explícitamente la regla de arriba y la revisión rechaza toda imagen con las hojitas sobre o a través del gorro.
  Pendiente (#17): una versión corregida de esa referencia o recortes de cara donde se vea el copete correcto.
- `personajes/FICHAS.md` y `personajes/hojas/` describen el diseño anterior: solo históricos.

## Texto para los prompts (inglés; copiar tal cual)
```
BABY hummingbird: magenta knitted beanie with pink stripes and a fluffy magenta pompom at the BACK; EXACTLY THREE SHORT thin green leaf
feathers (no taller than a third of the beanie) that grow from his FOREHEAD and peek out from UNDER the front brim of the beanie at the
front-center (never through the knitted fabric, never on top of the beanie, never on the side); round vivid-green plush body, soft yellow
belly, magenta eyes, pink cheeks, LONG thin straight navy-blue beak, peach-pink wings, purple feet.
MOM hummingbird: NO hat; crest of 5-6 separate matte leaf-shaped feathers with light tips, swept back (never a slick helmet, never spikes,
never a fan); long eyelashes, peach-pink wings fading to lilac, long thin straight navy-blue beak; always clearly BIGGER than the baby
(about 1.4x his height).
```
Negativo para video: `crest on top of the beanie, leaves growing through the hat, tall crest, more than three crest leaves, fan crest,
spiky crest, slick helmet hair, mom same size as baby`.
