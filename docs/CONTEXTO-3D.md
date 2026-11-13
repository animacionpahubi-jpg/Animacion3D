# Contexto del proyecto 3D (traspaso, 2026-11-11)

Lo que Claude tenía en su memoria local, para que viaje con el proyecto. Claude debe leerlo al empezar (lo indica `CLAUDE.md`).
Reglas de Kling: `prompts/lecciones-kling.md` (leer SIEMPRE antes de gastar unidades).

## Qué es y cómo nació
Proyecto independiente del 2D (no comparte código, git ni bot). Del 2D solo se LEE; nunca se escribe allí desde el 3D.
Se probó primero 3D real en Blender por código (5–6/10, se descartó) y luego video con IA. El flujo que funciona hoy es el de abajo.

## Flujo de producción (acordado el 2026-11-10)
1. **Guion (Claude):** ~25 s, 5 planos de 5 s, UNA acción por plano, en un solo set (fondos fijos en `fondos/`). Aplicar las reglas
   del 2D (`../ANIMACION-2D/docs/lecciones.md`): gancho en el cuadro 0, el protagonista provoca su problema, causa → efecto visible,
   método distinto para la solución, final tierno sin relleno.
2. **Imágenes clave (Codex = ChatGPT Go, gratis):** una por corte, sobre el fondo fijo, SIEMPRE con los personajes oficiales de
   `personajes/personajes_finales/` adjuntos (nunca `personajes/hojas/*.png`, diseños viejos). Cada imagen usa la anterior como
   referencia de continuidad. Comando:
   `codex exec -m gpt-5.6-luna --skip-git-repo-check -s workspace-write -i ref1.png -i ref2.png - < prompt.txt`
   (el modelo por defecto gpt-5.5 no sirve con cuenta ChatGPT; sale 1024x1536). Ejemplo completo: `capitulos/cap2-tu-puedes/claves.py`.
3. **Revisión estricta (Claude) ANTES de mostrar:** ampliar caras y comparar contra `personajes_finales` y `personajes/REGLAS.md` (manda REGLAS.md): copete del bebé = 3 hojitas CORTAS que
   nacen de la FRENTE bajo el borde del gorro (nunca atravesando la lana); gorro magenta a rayas con pompón ATRÁS; pico azul marino largo
   en diagonal; mamá sin gorro, cresta de 5–6 plumitas-hoja mate (nunca pelo liso tipo casco), mamá ≈1,4× el bebé; mismo lugar, cámara,
   luz y objetos entre imágenes seguidas; nada flota. Si algo falla, se rehace y no se muestra.
4. **Video (Kling API oficial, de pago):** `python src/kling_api.py NOMBRE inicio.png final.png "prompt" --segundos 5`
   (kling-v3, modo pro ≈ 1080p, sin audio; 0,8 unidades/s). Generar DE A UN plano y revisarlo antes del siguiente.
   Alternativa gratis y manual: Gemini Omni (plan Pro, ~5 videos cada 5 h, una conversación por parte, siempre con imagen de inicio;
   no se puede automatizar: va contra sus términos).
5. **Montaje (Remotion, `editor/`):** `npx remotion studio` (http://localhost:3000) y `npx remotion render <Id> salida.mp4`.
   Cada tramo con nombre; los defectos visuales cortos se ACELERAN (3x), no se cortan; si un tramo rompe la lógica de la historia se
   repite el plano. Mismo encuadre en todos los planos. Audio propio sintetizado (`src/audio_kit.py`), −17,5 a −18,5 LUFS
   (el wav mono sube ~3 dB al pasar a estéreo: `volume` 0,62–0,7). Ejemplos: `editor/src/TuPuedes.tsx` + `src/cap2_textos_audio.py`.

## Textos en pantalla
- Título-enseñanza, frase clave y cierre («¡Envíaselo a quien amas!») en estilo logo Pahubi (Fredoka, morado/crema), en zona segura
  (entre el 15 % superior y el 25 % inferior).
- Sonidos y emociones con la hoja del usuario, estilo cómic blanco: `assets/onomatopeyas/` (¡PUM!, ¿?, !, foco de idea, globo «…»,
  soplo, ZZZZZ, ¡OOPS!, ¡PLOP!…). El usuario prefiere SÍMBOLOS para emociones (sorpresa = «!» sobre quien se sorprende; idea = foco)
  y palabras solo para golpes. 3–5 por capítulo, nunca encima de una cara.

## Estado
- `capitulos/cap1-atrapa-la-gota/` v6 (Remotion) — primer capítulo con Kling, terminado.
- `capitulos/cap2-tu-puedes/salida/tu-puedes-v5.mp4` — «¡TÚ PUEDES!», terminado con las correcciones del usuario.
- Kling: paquete de prueba de 100 unidades comprado el 2026-11-11, **vence el 2026-12-11**; usadas 72 (quedan ~28 ≈ 1 capítulo).
  Después del 5.º paquete de prueba la unidad sube a ~$0,14. Saldo: `python -c "import sys;sys.path.insert(0,'src');import kling_api as k,time;n=int(time.time()*1000);print(k.pedir(f'/account/costs?start_time={n-86400000*30}&end_time={n}'))"`.
- fal.ai sin saldo. Remotion: gratis solo para empresas de hasta 3 empleados (confirmar si aplica a Pahubi antes de publicar).
- Repositorio: ver la sección «Repositorio» al final.

## Repositorio
`https://github.com/animacionpahubi-jpg/Animacion3D` (rama `main`). No se suben: `.env`, `node_modules` (reinstalar con
`cd editor && npm i`), los `.blend` del experimento Blender, `assets/polyhaven/` y las versiones viejas de los capítulos.
Remotion lee los clips desde `editor/public/` (no versionados): copiarlos antes de abrir el Studio, p. ej.
`cp pruebas/ia/cap2-*.mp4 pruebas/ia/cap1-A3.mp4 pruebas/ia/cap1-B2.mp4 pruebas/ia/cap1-C2.mp4 editor/public/`.
