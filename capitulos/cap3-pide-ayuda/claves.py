"""Imágenes clave de «¡PIDE AYUDA!» con Codex, en orden, cada una con la anterior como referencia de continuidad."""
import pathlib, subprocess
R = pathlib.Path(__file__).resolve().parents[2]; K = pathlib.Path(__file__).parent
P = "personajes/personajes_finales"; FONDO = "fondos/f1-flor-hibisco.png"
OFICIAL = [f"{P}/bebe-pose.jpg", f"{P}/bebe-expresiones.jpg", f"{P}/mama-vistas.jpg", f"{P}/mama-pose.jpg"]
COMUN = """Characters EXACTLY like the official character images attached (never invent a design):
- BABY: magenta knitted beanie with pink stripes and a fluffy magenta pompom at the BACK; three thin green leaf feathers growing from his FOREHEAD,
  peeking out from UNDER the front brim of the beanie at the front-center (never through the knit, never on the side, never on top of the beanie);
  round vivid-green plush body, soft yellow belly, magenta eyes, pink cheeks, LONG thin straight navy-blue beak (three-quarter view so it reads long),
  peach-pink wings, purple feet.
- MOM: NO hat; soft crest of 5-6 separate matte leaf feathers with light tips (never a slick helmet, never spikes); long eyelashes,
  peach-pink wings fading to lilac; always clearly BIGGER than the baby (about 1.4x).
SET: the attached background f1-flor-hibisco.png: same dirt path, same big pink hibiscus on its stem at the right, same golden sunrise backlight.
The hibiscus is TALL: its flower is well above the baby's head. Nothing floats. High-end 3D animated film look (Pixar-like), soft plush textures,
warm golden rim light. Portrait 1024x1536. No text."""
CLAVES = [
 ("k2", None, "MEDIUM-WIDE SHOT of the set. The baby SITS on his bottom on the dirt path, just below and left of the tall hibiscus, legs forward, a bit surprised and dazed after a little fall, looking UP at the flower that is out of his reach. Only the baby."),
 ("k1", "k2", "CLOSER SHOT of the same place (same light, same flower): the baby stands on the TIPS of his toes on the path, stretching his neck and long beak UP toward the tall hibiscus with longing eyes, but the flower is still clearly out of reach above him; he leans and starts to wobble. Only the baby. Leave the upper area calm for a title."),
 ("k3", "k2", "Same MEDIUM-WIDE SHOT as k2. The baby still SITS on the path, looking up and to the LEFT at mom, beak slightly open as if calling her, hopeful face. Mom hovers in the air at the LEFT of the baby, a bit higher than him, wings in a fast blur, smiling tenderly at him. The flower stays tall at the right."),
 ("k4", "k3", "Same MEDIUM-WIDE SHOT as k3. Mom hovers next to the hibiscus and gently bends its stem DOWN with the tip of her wing, so the flower is now right in front of the baby's face. The baby now STANDS and drinks nectar happily, the tip of his long beak touching the center of the flower, eyes half closed with joy. Mom smiles."),
 ("k5", "k4", "Same MEDIUM-WIDE SHOT as k4. Mom has let go of the flower (the hibiscus is back up in its original tall place) and has landed beside the baby on the path; they HUG tenderly, eyes closed, smiling. Mom's wing wraps around him; her cheek rests on top of his beanie and her long beak points UP and AWAY over his head (it never touches him; beaks never cross)."),
]
for nombre, prev, desc in CLAVES:
    out = K / f"{nombre}.png"
    if out.exists(): continue
    refs = [FONDO] + ([str((K / f"{prev}.png").relative_to(R))] if prev else []) + OFICIAL
    orden = "Attached, in order: background f1-flor-hibisco.png" + (f", previous keyframe {prev}.png (keep its place, light, camera, character sizes and designs)" if prev else "") + ", then the official character images."
    txt = f"Use your image generation tool to create ONE image and save it as {out.relative_to(R).as_posix()}.\n{orden}\nSHOT: {desc}\n{COMUN}"
    args = ["codex.cmd", "exec", "-m", "gpt-5.6-luna", "--skip-git-repo-check", "-s", "workspace-write"]
    for r in refs: args += ["-i", r]
    subprocess.run(args + ["-"], input=txt, cwd=R, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    print(nombre, "ok" if out.exists() else "FALLÓ", flush=True)
