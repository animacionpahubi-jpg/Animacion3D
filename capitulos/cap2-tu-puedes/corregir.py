import pathlib, subprocess
R = pathlib.Path(__file__).resolve().parents[2]; K = pathlib.Path(__file__).parent
P = "personajes/personajes_finales"
CRESTA = ("CRITICAL DETAIL: the baby's three thin green leaf feathers grow from his FOREHEAD, just BELOW the front edge (brim) of the beanie, "
          "peeking out from under the brim at the front-center of his head, exactly like in the attached reference k5.png. They NEVER grow out of the "
          "knitted fabric and never sit on top of the beanie. Magenta beanie with pink stripes, pompom at the BACK. Long thin straight navy-blue beak.")
TAREAS = [
 ("k3", ["k3_v1", "k5"], "Edit the first attached image (k3_v1.png): keep EVERYTHING identical (place, camera, light, mom, the baby's belly-down pose on the leaf, his face) and ONLY fix the baby's leaf feathers. " + CRESTA),
 ("k4", ["k4_v1", "k5"], "Edit the first attached image (k4_v1.png): keep EVERYTHING identical (place, camera, light, mom, the baby sitting dizzy with the little stars) and ONLY fix the baby's leaf feathers. " + CRESTA),
 ("k1", ["k2", "k5"], "CLOSE-UP of the baby from the first attached image (k2.png): same leaf at the upper right, same light, same camera direction. Only the baby, from the chest up, in the lower-middle of the frame, FACING LEFT exactly like in k2 (his long beak points down-LEFT over the leaf edge), very scared: big worried eyes, wings trembling. Mom is NOT in this frame. Keep the upper third calm (sky/bokeh) for a title. Portrait 1024x1536, Pixar-like 3D, golden sunrise backlight. " + CRESTA),
]
for nombre, refs, txt in TAREAS:
    out = K / f"{nombre}.png"
    if out.exists(): continue
    args = ["codex.cmd", "exec", "-m", "gpt-5.6-luna", "--skip-git-repo-check", "-s", "workspace-write"]
    for r in refs: args += ["-i", str((K / f"{r}.png").relative_to(R))]
    args += ["-i", f"{P}/bebe-pose.jpg", "-i", f"{P}/bebe-expresiones.jpg", "-"]
    prompt = f"Use your image generation tool to create ONE image and save it as {out.relative_to(R).as_posix()}.\n{txt}\nNo text."
    subprocess.run(args, input=prompt, cwd=R, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    print(nombre, "ok" if out.exists() else "FALLÓ", flush=True)
