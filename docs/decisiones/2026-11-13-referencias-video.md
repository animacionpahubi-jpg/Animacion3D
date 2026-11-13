# Decisión: cómo se mantiene al personaje en el video (referencias fijas vs. imagen inicial + final)
**Fecha:** 2026-11-13 · **Tarea:** #13 (HU #12) · **Estado:** decidido

## Contexto
El 7 y el 9 de noviembre se probó el enfoque de **referencias fijas** con fal.ai (`src/fal_video.py`): una **previz gris de Blender**
(`src/guia_plano_hoja.py` → `pruebas/guia-hoja*.mp4`) marcaba cámara y movimiento, y el modelo la «pintaba» con la hoja del personaje.
Después el proyecto pasó a **imagen inicial + final con Kling v3** (imágenes clave de Codex), sin que quedara escrito por qué.
Esta revisión no gastó unidades: se compararon las hojas de cuadros de los videos existentes.

## Resultados de las pruebas
Las cuatro usaron el **diseño anterior** del bebé (`personajes/hojas/bebe-hoja.png`: gorro morado, pico azul pizarra), reemplazado el
2026-11-10 por `personajes/personajes_finales/`. Plano de prueba: el bebé entra volando, se posa en la hoja y se asoma a la gota.

| Prueba | Modelo (fal.ai) | Costo 5 s | Resolución | Sigue la previz | Identidad | Copete |
|---|---|---|---|---|---|---|
| `hoja-kling` | Kling O3 video-to-video/reference con `@Element1` (cara + hoja) | USD 0,63 | 720×1280 | Sí, fiel | Buena y estable | **Mal**: sale de atrás / del lado del gorro |
| `hoja-wan480` | Wan 3.0 reference-to-video | USD 0,25 | 480×854 | Sí, fiel | Buena, textura 3D rica | **Mal**: desaparece |
| `hoja-seedance20mini` | Seedance 2.0 mini reference-to-video | USD 0,40 | 496×864 | Sí, fiel | Buena, más «pastel» | Al costado del gorro, estable |
| `hoja-seedance25-borrador` | Seedance 2.5 editing (borrador) | USD 1,23 | 480×854 | Sí, fiel | Muy buena luz | Delante, a un costado |
| **Actual** `cap2-P4` | Kling v3 pro, inicio + final (API oficial) | ~USD 0,39 (4 u) | **1176×1764** | — (manda la imagen final) | Buena, set fijo | Depende de la imagen clave |

Hojas de cuadros (1,6 cuadros/s): previz `img/2026-11-13-guia-color.jpg` · `img/2026-11-13-hoja-kling.jpg` · `img/2026-11-13-hoja-wan480.jpg` ·
`img/2026-11-13-hoja-seedance20mini.jpg` · `img/2026-11-13-hoja-seedance25-borrador.jpg` · actual `img/2026-11-13-cap2-P4.jpg`.

**Lo que se aprendió**
- La guía de movimiento funciona: los cuatro modelos respetan cámara, tiempos y posiciones de la previz.
- **Ninguna referencia (ni `@Element`) resolvió el copete**: cada modelo lo puso en otro lugar. Las referencias solas no garantizan los
  detalles finos; hace falta definir el rasgo (`personajes/REGLAS.md`) y auditarlo (#14).
- Salida en baja resolución (480–720p) frente a ~1080p del flujo actual.

## Por qué se descartó (confirmado por el equipo)
- **La previz era muy costosa**: cada plano exigía construir y animar una escena en Blender a mano (solo `guia_plano_hoja.py` son
  148 líneas para un plano de 5 s). Con imágenes clave de Codex (gratis, minutos por imagen) se controla la composición sin ese trabajo.

## Decisión
**(a) Seguir con imagen inicial + final con Kling v3** y continuar la producción con el **cap3** (el cap2 está terminado).
- Rinde: 1,40 intentos por plano en cap2 (2,33 en cap1), ~28 u por capítulo de 5 planos en pro.
- El copete y las proporciones se atacan **antes** de Kling, en las imágenes clave: reglas en `personajes/REGLAS.md`, referencia
  corregida `bebe-pose-corregida.png` y auditoría de identidad (#14), donde rehacer es gratis.
- **Continuidad entre planos** (pendiente, #3): el último cuadro aprobado del plano N pasa a ser la imagen inicial del N+1.
- **Elements / `@Element` (b)**: no ahora. Solo una prueba controlada cuando haya un paquete de Kling nuevo (#4), verificando
  antes el endpoint y los límites en la API oficial.
- **Previz / guía estructural (c)**: descartada como vía principal por costo; #15 sigue como experimento condicionado, solo si una
  guía se puede generar sin construir escenas a mano.

## Restricción de gasto
Quedan **11 unidades** (88,5 % consumido; vence el 2026-12-11). El cap3 (4 planos de 5 s en std ≈ 3 u por intento) necesita
~12 u si todo sale a la primera y ~17 u al ritmo del cap2: **no alcanza sin un paquete nuevo**. Las imágenes clave (Codex) sí se
pueden hacer y auditar ya, sin gastar unidades.
