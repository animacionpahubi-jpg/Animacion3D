"""Imágenes clave de «¡TÚ PUEDES!» con Codex (ChatGPT Go), en orden, cada una con la anterior como referencia de continuidad."""
import pathlib, subprocess, sys
R = pathlib.Path(__file__).resolve().parents[2]; K = pathlib.Path(__file__).parent
P = "personajes/personajes_finales"
OFICIAL = [f"{P}/bebe-pose.jpg", f"{P}/bebe-expresiones.jpg", f"{P}/mama-vistas.jpg", f"{P}/mama-pose.jpg"]
COMUN = """Characters must look EXACTLY like the official character images attached (never invent a design):
- BABY hummingbird: magenta knitted beanie with pink stripes and a fluffy magenta pompom at the BACK; three thin green leaf feathers that grow
  from his FOREHEAD at the front edge of the beanie (never through the knit, never on the side); round vivid-green plush body, soft yellow belly,
  magenta eyes, pink cheeks, LONG thin straight navy-blue beak (three-quarter view so the beak reads long and diagonal), peach-pink wings, purple feet.
- MOM hummingbird: NO hat; soft crest of 5-6 separate matte leaf feathers with light tips (never a slick helmet, never spikes); long eyelashes,
  peach-pink wings fading to lilac; always clearly BIGGER than the baby (about 1.4x).
Background: use the attached background f2-hojas-rocio.png as the set: same place, same golden sunrise backlight, same leaves; dew drops stay
ON the leaves; REMOVE the single drop floating in mid-air. High-end 3D animated feature film look (Pixar-like), soft plush textures,
warm golden rim light. Portrait 1024x1536. No text."""
CLAVES = [
 ("k2", "fondos/f2-hojas-rocio.png", None, "MEDIUM SHOT of the set. The baby stands on the tip of the leaf at the upper RIGHT, looking DOWN over the edge, scared: big worried eyes, wings trembling close to his body. Mom hovers in the air just to his LEFT at the same height, wings spread in a fast blur, smiling encouragingly at him. Below them, at the lower LEFT, the big dewy leaf of the background is clearly visible (he will fall onto it later)."),
 ("k1", "fondos/f2-hojas-rocio.png", "k2", "CLOSE-UP of the baby from image k2 (same leaf, same light): only the baby, from the chest up, filling the lower-middle of the frame, looking down over the leaf edge, very scared: big wet worried eyes, little beak pointing down, wings trembling. Mom is NOT in this frame. Leave the upper third of the image calm (sky/bokeh) for a title."),
 ("k3", "fondos/f2-hojas-rocio.png", "k2", "WIDE SHOT of the same set as k2 (same camera). The baby has fallen and landed BELLY-DOWN on the big dewy leaf at the lower LEFT: wings spread out, feet up, surprised funny face, the leaf bent down a little under him. Mom hovers up near the upper right leaf looking down at him, surprised. Nothing is broken, he is fine."),
 ("k4", "fondos/f2-hojas-rocio.png", "k3", "Same WIDE SHOT as k3. The baby now SITS on the big dewy leaf at the lower LEFT, laughing happily, a bit dizzy from bouncing. Mom has flown down and hovers in the air right beside him (to his right), wings in a fast blur, smiling and showing him her wings."),
 ("k5", "fondos/f2-hojas-rocio.png", "k4", "Same WIDE SHOT as k4. The baby is FLYING: he hovers in the air just above the big dewy leaf, his little wings in a very fast blur, proud big smile, determined eyes. Mom hovers beside him at the same height, delighted. Both clearly in the air (the leaf is empty below him)."),
 ("k6", "fondos/f2-hojas-rocio.png", "k5", "Same WIDE SHOT as k5. Mom and baby have landed together on the big dewy leaf and HUG tenderly, eyes closed, smiling. Mom's wing wraps around him; her cheek rests on top of his beanie and her long beak points UP and AWAY over his head (it never touches him; beaks never cross). The baby's wings still buzz a little with excitement and his beanie is pushed up a tiny bit (cute joke)."),
]
for nombre, fondo, prev, desc in CLAVES:
    out = K / f"{nombre}.png"
    if out.exists(): continue
    refs = [fondo] + ([str((K / f"{prev}.png").relative_to(R))] if prev else []) + OFICIAL
    orden = "Attached, in order: background f2-hojas-rocio.png" + (f", previous keyframe {prev}.png (keep its place, light, camera, character sizes and designs)" if prev else "") + ", then the official character images."
    txt = f"Use your image generation tool to create ONE image and save it as {out.relative_to(R).as_posix()}.\n{orden}\nSHOT: {desc}\n{COMUN}"
    args = ["codex.cmd", "exec", "-m", "gpt-5.6-luna", "--skip-git-repo-check", "-s", "workspace-write"]
    for r in refs: args += ["-i", r]
    subprocess.run(args + ["-"], input=txt, cwd=R, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    print(nombre, "ok" if out.exists() else "FALLÓ", flush=True)
