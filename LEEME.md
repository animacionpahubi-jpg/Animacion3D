# Animacion-3D
Guía de traspaso completa: ../ANIMACION-2D/ONBOARDING.md · Contexto de este proyecto: docs/CONTEXTO-3D.md
Abre ../Pahubi.code-workspace en VS Code para tener los dos proyectos juntos.

## Instalar el entorno (una vez por PC)
Se trabaja desde la carpeta del workspace (`trabajo/`, la que contiene `ANIMACION-2D/` y `Animacion3D/`).

1. **Python 3.10 o más reciente** y el entorno compartido del workspace (los paquetes del 3D están en `Animacion3D/requirements.txt`):
   ```
   python -m venv .venv
   .venv\Scripts\python -m pip install -r requirements.txt
   ```
   Para instalar solo el 3D: `python -m venv .venv` dentro de `Animacion3D/` y `pip install -r requirements.txt` (ese `.venv` está ignorado en git).
2. **ffmpeg**: no se instala aparte; viene con el paquete `imageio-ffmpeg` y los scripts lo encuentran con `imageio_ffmpeg.get_ffmpeg_exe()`.
3. **Node 24 LTS** (mínimo 20.19) y Remotion: `cd Animacion3D/editor && npm i`.
4. **Codex** (imágenes clave, se descuentan del plan de ChatGPT Go o superior). Dos formas:
   - **App de escritorio de Codex** (la de este PC): trae su propio binario en `%USERPROFILE%\.codex\plugins\.plugin-appserver\codex.exe`,
     que `verificar_entorno.py` detecta solo. Iniciar sesión en la app con la cuenta de la empresa.
   - **CLI por npm:** `npm i -g @openai/codex` y `codex login` con la cuenta de la empresa.
   Si el binario no está en el PATH, definir la variable `CODEX_BIN` con su ruta. Los `claves.py` actuales lo llaman como
   `codex.cmd exec -m gpt-5.6-luna ...` (el modelo por defecto no sirve con cuenta ChatGPT); la interfaz única de proveedores es la tarea #18.
5. **Claves** en `Animacion3D/.env` (nunca en git ni en el chat): `KLING_API_KEY` es obligatoria; `GEMINI_API_KEY` y las de Cloudflare son opcionales
   y, si faltan, se leen de `ANIMACION-2D/.env`.
6. **Comprobar**: `.venv\Scripts\python Animacion3D/src/verificar_entorno.py` → debe terminar en «Listo para producir». No muestra valores de claves.

## Herramientas de revisión
- Hoja de cuadros de un plano: `python src/tira.py cap2-P4 salida.png` (busca `pruebas/ia/cap2-P4.mp4`).
- Voces de un clip: `python src/transcribir.py pruebas/ia/NOMBRE.mp4`.
