# Lecciones de Kling (API oficial, kling-v3 pro) — leer ANTES de gastar unidades

Origen: «¡Atrapa la gota!» (2026-11-11). Se gastaron 36 unidades en 6 tomas y solo 1 plano salió aprobado a la primera
(ninguno, en realidad: A al 3.er intento, B al 2.º con un defecto, C rechazado). Precio: 0,8 unidades/s a 1080p (≈ $0,078/s).

## Qué falla (no pedírselo)
1. **Líquidos y gotas**: las gotas se estiran como hilo de goma, cuelgan de un «hilo» desde el cielo, los chorros salen como cuerdas.
   Una gota que cae de A a B es el peor caso. Si la historia necesita agua, que sea quieta (charco, rocío pegado) o se dibuja en el montaje.
2. **Cambios de estado** que no están en las imágenes (lavar el barro, secarse, que algo aparezca): Kling los invierte o los multiplica
   (el barro AUMENTÓ en vez de lavarse). El estado debe ser IGUAL en la imagen inicial y la final.
3. **Varias acciones en un plano** (tocar la flor + ducha + lavado + abrazo en 10 s): hace la mitad y mal. Una acción por plano.
4. **Partes que no se ven en las imágenes** (espalda, cola): las inventa (cola azul de pavo real, ala turquesa). Cámara de frente o
   de lado; si el personaje se da vuelta, describir la cola/espalda en el prompt.
5. **Abrazos**: el pico de mamá va a la cara del bebé si la imagen final no lo deja muy claro. La imagen final manda.

## Qué funciona
- Imagen inicial + final del MISMO set y cámara, con los personajes ya en su estado final: el plano llega a la imagen final fiel.
- Movimientos simples: mirar, reír, parpadear, volar de un punto a otro, entrar a cuadro, abrazar.
- Negativo específico (`NEGATIVO` en src/kling_api.py) con cada defecto visto.

## Cómo gastar menos
1. **Guion para Kling**: cada plano = una acción simple sin líquidos ni transformaciones. Si un efecto es difícil, lo resuelve el
   montaje (gotitas dibujadas, corte) o se cambia la historia ANTES de generar.
2. **Imágenes clave primero** (Codex, gratis): todo cambio de estado se dibuja en una imagen clave, no se le pide a Kling.
3. **De a un plano**: generar, revisar, y solo entonces el siguiente. Nunca lanzar dos planos a la vez si el segundo depende de una idea
   no probada.
4. **Planos de 5 s** cuando alcance; 10 s solo si la acción es una sola y lenta.
5. **Presupuesto por capítulo**: ~25 unidades (3 planos + 1 repetición). Si un plano falla 2 veces, se cambia la acción, no se insiste.
6. Un defecto corto (< 0,5 s) se recorta en el montaje en vez de repetir el plano (en Remotion: acelerarlo a 3x, no cortarlo con
   fundido, para que el movimiento siga continuo).

## Lógica de la historia («¡TÚ PUEDES!», 2026-11-11, observación del usuario)
- Kling EXAGERA los movimientos amplios: un «rebote en la hoja» salió como subir volando hasta mamá (y el bebé aún no sabía volar).
  Nada de rebotes, saltos altos ni vueltas: acciones contenidas (levantarse, sacudir la cabeza, caer de panza).
- Acelerar un tramo (3x) solo sirve para defectos VISUALES cortos (un pico que roza). Si el tramo rompe la lógica de la historia
  (alguien vuela cuando no sabe, algo aparece sin causa), se repite el plano.
- Un estado nuevo (mareado, mojado, triste) debe EMPEZAR dentro del plano, causado por algo que se ve; si viene ya dibujado en la
  imagen final, aparece «de la nada» (regla 28 del 2D).
- Revisión final: ver el video completo como espectador (¿se entiende por qué pasa cada cosa?), no solo cada plano por separado.

## Ritmo y coherencia (comparación v2 fal.ai vs v6, 2026-11-11)
El v2 se sentía más fluido con el MISMO modelo porque: 4 planos de 5 s (uno por acción), 6 imágenes clave (una cada ~4 s), tiempos
muertos recortados y tomas más cercanas. El v6 tuvo planos de 10 s con ~4 s de espera y solo 4 imágenes clave para 25 s.
- Un plano = 5 s = una acción; una imagen clave por plano (Codex, gratis). Imagen inicial y final PARECIDAS → Kling no inventa.
- Recortar en el montaje todo segundo en que no pasa nada (pasa algo nuevo cada 3–5 s).
- Alternar plano cercano y abierto sobre el fondo fijo; nunca terminar con una imagen fija (se nota el salto).
- 5 planos × 5 s ≈ 20 unidades por capítulo.
