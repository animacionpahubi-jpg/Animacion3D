"""Guía de movimiento (Fase 1.1) — plano de prueba «el colibrí bebé se asoma a la hoja con la gota de rocío».
No es la imagen final: define movimiento, cámara y composición para que la IA de video la pinte con la hoja de personaje.
Personaje: el de src/colibri_bebe.py (solo su parte de personaje). Cielo CC0 de Poly Haven (spruit_sunrise).
Uso:
  blender -b -P src/guia_plano_hoja.py -- salida.mp4            → video 720x1280, 24 fps, 5 s (EEVEE)
  blender -b -P src/guia_plano_hoja.py -- carpeta/ --cuadros 1,60,120   → solo esos cuadros en PNG (revisión)
"""
import bpy, math, sys, pathlib
import numpy as np
from mathutils import Vector

RAIZ = pathlib.Path(__file__).resolve().parents[1]
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SALIDA = args[0] if args else str(RAIZ / "pruebas" / "guia-hoja.mp4")
CUADROS = [int(x) for x in args[args.index("--cuadros") + 1].split(",")] if "--cuadros" in args else None
FPS, DUR = 24, 5.0
N = int(FPS * DUR)

fuente = (RAIZ / "src" / "colibri_bebe.py").read_text(encoding="utf-8")
g = {"__file__": str(RAIZ / "src" / "colibri_bebe.py"), "__name__": "personaje"}
exec(compile(fuente.split("# --- escenario")[0], "colibri_bebe.py", "exec"), g)
esc, col, mat, esfera, pj = g["esc"], g["col"], g["mat"], g["esfera"], g["pj"]
esc.render.fps = FPS; esc.frame_start, esc.frame_end = 1, N

# --- cielo de amanecer con el sol arriba a la derecha, detrás de la escena ------------------------
hdr = next((RAIZ / "assets" / "polyhaven" / "spruit_sunrise").glob("*.hdr"))
img = bpy.data.images.load(str(hdr)); W, Hh = img.size
px = np.empty(W * Hh * 4, dtype=np.float32); img.pixels.foreach_get(px)
fila, colu = np.unravel_index(np.argmax(px.reshape(Hh, W, 4)[..., :3].sum(axis=2)), (Hh, W))
az_sol = ((colu + 0.5) / W - 0.5) * 2 * math.pi
deseado = math.atan2(1.0, -0.55)                       # sol detrás y a la derecha (x=0.55, y=1)
w = bpy.data.worlds.new("amanecer"); esc.world = w; w.use_nodes = True
nt = w.node_tree; bg = nt.nodes["Background"]; bg.inputs["Strength"].default_value = 1.0
tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); env = nt.nodes.new("ShaderNodeTexEnvironment")
env.image = img; mp.inputs["Rotation"].default_value[2] = -(deseado - az_sol)
nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
nt.links.new(env.outputs["Color"], bg.inputs["Color"])
sol = bpy.data.lights.new("sol", "SUN"); sol.energy = 3.5; sol.color = (1.0, 0.78, 0.5); sol.angle = math.radians(4)
so = bpy.data.objects.new("sol", sol); col.objects.link(so)
so.rotation_euler = (-Vector((0.55, 1.0, 0.25)).normalized()).to_track_quat("-Z", "Y").to_euler()
d = bpy.data.lights.new("relleno", "AREA"); d.energy = 250; d.size = 3; d.color = (1.0, 0.9, 0.78)
ro = bpy.data.objects.new("relleno", d); col.objects.link(ro); ro.location = (-1.5, -4.0, 2.5)
ro.rotation_euler = (Vector((0, 0, 0.6)) - ro.location).to_track_quat("-Z", "Y").to_euler()

# --- hoja grande en primer plano con nervadura y gota de rocío ------------------------------------
HOJA = mat("hoja_grande", (0.10, 0.38, 0.05), rough=0.35, sss=0.25, coat=0.4)
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1, location=(-0.35, -0.55, 0.05))
hoja = bpy.context.object; hoja.name = "hoja"; hoja.scale = (1.9, 0.75, 0.035)
hoja.rotation_euler = (math.radians(42), math.radians(6), math.radians(12)); bpy.ops.object.shade_smooth()
dobla = hoja.modifiers.new("curva", "SIMPLE_DEFORM"); dobla.deform_method = "BEND"; dobla.angle = math.radians(35); dobla.deform_axis = "Y"
hoja.data.materials.append(HOJA)
NERV = mat("nervio", (0.35, 0.62, 0.18), rough=0.5)
bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.012, depth=3.4, location=(-0.35, -0.55, 0.09), rotation=(0, math.radians(90), 0))
nerv = bpy.context.object; nerv.data.materials.append(NERV); nerv.parent = hoja; nerv.matrix_parent_inverse = hoja.matrix_world.inverted()
AGUA = bpy.data.materials.new("gota"); AGUA.use_nodes = True
pa = AGUA.node_tree.nodes["Principled BSDF"]; pa.inputs["Transmission Weight"].default_value = 1.0; pa.inputs["Roughness"].default_value = 0.0; pa.inputs["IOR"].default_value = 1.33
gota = esfera("gota", (-0.12, -0.28, 0.45), 0.10, (1, 1, 0.85), AGUA, seg=48)

# fondo: masas de follaje desenfocadas
FOLL = [mat(f"foll{k}", c, rough=0.7, sheen=0.4) for k, c in enumerate(((0.06, 0.22, 0.03), (0.12, 0.32, 0.05), (0.20, 0.40, 0.08)))]
import random
random.seed(3)
for k in range(28):
    esfera(f"follaje{k}", (random.uniform(-9, 9), random.uniform(9, 20), random.uniform(-3.0, 3.5)), random.uniform(1.0, 2.4),
           (1, 0.7, 0.8), FOLL[k % 3], seg=24)

# --- animación del colibrí -------------------------------------------------------------------------
# entra volando desde arriba a la derecha, frena flotando y se asoma detrás del borde de la hoja, pico hacia la gota
pj.rotation_mode = "XYZ"
claves = [  # (cuadro, posición, giro z en grados, inclinación del cuerpo en grados)
    (1,   (2.4, 1.0, 1.9), 205, -20),
    (40,  (1.05, 0.55, 0.95), 200, -12),
    (62,  (0.55, 0.32, 0.50), 198, -4),    # frena
    (78,  (0.42, 0.28, 0.40), 196, 4),     # flota detrás del borde de la hoja
    (86,  (0.42, 0.28, 0.44), 196, 4),
    (100, (0.36, 0.26, 0.24), 194, 22),    # baja y se inclina: asoma la cabeza, pico hacia la gota
    (120, (0.36, 0.26, 0.25), 194, 20),
]
for f, pos, rz, ry in claves:
    pj.location = pos; pj.rotation_euler = (0, math.radians(ry), math.radians(rz))
    pj.keyframe_insert("location", frame=f); pj.keyframe_insert("rotation_euler", frame=f)
for fc in pj.animation_data.action.fcurves if hasattr(pj.animation_data.action, "fcurves") else []:
    for k in fc.keyframe_points: k.interpolation = "BEZIER"; k.easing = "EASE_IN_OUT"
pj.scale = (0.55, 0.55, 0.55)

# vaivén suave mientras flota (modificador de ruido en la altura)
try:
    for fc in pj.animation_data.action.fcurves:
        if fc.data_path == "location" and fc.array_index == 2:
            m = fc.modifiers.new("NOISE"); m.scale = 10; m.strength = 0.05
except Exception as ex:
    print("sin vaivén:", ex)

# aleteo: las plumas de las alas giran rápido (zumbido de colibrí) mientras vuela; casi quietas al final
for o in [o for o in bpy.data.objects if o.name.startswith("ala")]:
    base = o.rotation_euler.copy(); lado = 1 if o.name[3] != "-" else -1
    for f in range(1, N + 1, 2):
        amp = 0.9 if f < 96 else 0.12
        fase = 1 if (f // 2) % 2 == 0 else -1
        o.rotation_euler = (base.x + lado * amp * fase, base.y, base.z)
        o.keyframe_insert("rotation_euler", frame=f)

# --- cámara: se acerca despacio, desenfoque fuerte -------------------------------------------------
cd = bpy.data.cameras.new("cam"); cd.lens = 50; cd.dof.use_dof = True; cd.dof.aperture_fstop = 0.5
cam = bpy.data.objects.new("cam", cd); col.objects.link(cam); esc.camera = cam
foco = bpy.data.objects.new("foco", None); col.objects.link(foco)
for f, pos_c, pos_f in ((1, (0.1, -4.6, 1.35), (0.5, 0.0, 0.75)), (N, (0.22, -3.4, 1.05), (0.22, -0.1, 0.45))):
    cam.location = pos_c; foco.location = pos_f
    cam.keyframe_insert("location", frame=f); foco.keyframe_insert("location", frame=f)
tr = cam.constraints.new("TRACK_TO"); tr.target = foco; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"
cd.dof.focus_object = pj

# --- modo «arcilla» (como el previz del video 3): todo gris liso, sin colores ni ojos ni cielo ------
# Así la IA de video solo toma de la guía el movimiento, la cámara y las formas; el aspecto lo saca de la hoja de personaje.
if "--gris" in args:
    ARCILLA = mat("arcilla", (0.42, 0.42, 0.42), rough=0.7)
    for o in bpy.data.objects:
        if o.type in ("MESH", "META", "CURVE"):
            o.data.materials.clear(); o.data.materials.append(ARCILLA)
            for ms in getattr(o, "particle_systems", []): ms.settings.material = 1
    for m in list(cuerpo_hair := [o for o in bpy.data.objects if o.name == "cuerpo"]):
        for mod in list(m.modifiers):
            if mod.type == "PARTICLE_SYSTEM": m.modifiers.remove(mod)   # sin plumón: forma limpia
    w.node_tree.links.clear() if False else None
    bg.inputs["Color"].default_value = (0.55, 0.55, 0.55, 1)
    for l in list(nt.links):
        if l.to_node == bg: nt.links.remove(l)
    cd.dof.use_dof = False

# --- render ----------------------------------------------------------------------------------------
esc.render.engine = "BLENDER_EEVEE"
esc.render.resolution_x, esc.render.resolution_y = 720, 1280
esc.view_settings.view_transform = "AgX"; esc.view_settings.look = "AgX - Medium High Contrast"
pathlib.Path(SALIDA).parent.mkdir(parents=True, exist_ok=True)
if CUADROS:
    esc.render.image_settings.file_format = "PNG"
    for f in CUADROS:
        esc.frame_set(f); esc.render.filepath = str(pathlib.Path(SALIDA) / f"cuadro-{f:03d}.png")
        bpy.ops.render.render(write_still=True)
else:
    try: esc.render.image_settings.media_type = "VIDEO"
    except Exception: pass
    esc.render.image_settings.file_format = "FFMPEG"
    esc.render.ffmpeg.format = "MPEG4"; esc.render.ffmpeg.codec = "H264"; esc.render.ffmpeg.constant_rate_factor = "HIGH"
    esc.render.filepath = SALIDA
    bpy.ops.render.render(animation=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(pathlib.Path(SALIDA).with_suffix(".blend")))
print("LISTO", SALIDA)
