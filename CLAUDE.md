# Instrucciones permanentes para Claude (Pahubi Animación 3D)
Responde siempre en español. No instales nada sin avisar. Usa solo recursos propios o con licencia.

0. **Al empezar, lee `docs/CONTEXTO-3D.md`** (flujo, estado, pendientes) y, antes de gastar unidades de Kling, `prompts/lecciones-kling.md`.
1. **Proyecto independiente.** Animacion-3D NO comparte código, configuración, producción nocturna, bot ni git con ANIMACION-2D.
   Del 2D (`../ANIMACION-2D`) solo se LEE como referencia (`docs/01-ESTANDAR.md`, `docs/lecciones.md`, `config/reglas-contenido.yml`).
   Nunca escribir, mover ni borrar nada dentro de ANIMACION-2D desde este proyecto. Si algo del 2D sirve, se COPIA aquí.
2. Mismos personajes: "colibrí bebé", "mamá colibrí", "pollito". Nunca "Pío". Diseño oficial: SOLO `personajes/personajes_finales/`.
3. Contenido apto para toda la familia (mismas reglas que el 2D: sin política, religión, ideología, burlas, violencia real, miedo intenso,
   marcas ajenas, material con derechos de terceros). Marca Pahubi solo discreta.
4. Herramientas actuales: Codex CLI (imágenes clave, cuenta ChatGPT), Kling API (`src/kling_api.py`, de pago), Remotion (`editor/`, montaje),
   audio propio (`src/audio_kit.py`). Blender (`src/colibri_bebe.py`) quedó como experimento descartado.
5. Revisión estricta: rechazar y rehacer imágenes o planos con incongruencias ANTES de mostrarlos (lista en `docs/CONTEXTO-3D.md`).
6. Claves solo en `.env` (nunca imprimirlas ni pedirlas por chat).
