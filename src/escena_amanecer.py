"""Colibrí bebé en un amanecer de selva (prueba de ambiente v1) — Pahubi Animación 3D.
Reutiliza el personaje de src/colibri_bebe.py y monta el ambiente con recursos CC0 de Poly Haven
(cielo HDRI spruit_sunrise, tronco con musgo, helechos, plantas de selva y árboles; ver src/polyhaven.py).
Uso:  blender -b -P src/escena_amanecer.py -- salida.png [muestras]
"""
import bpy, math, sys, pathlib, random
import numpy as np
from mathutils import Vector

RAIZ = pathlib.Path(__file__).resolve().parents[1]
PH = RAIZ / "assets" / "polyhaven"
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SALIDA = args[0] if args else str(RAIZ / "pruebas" / "amanecer-v1.png")
MUESTRAS = int(args[1]) if len(args) > 1 else 128

# personaje: se ejecuta solo la parte de colibri_bebe.py hasta antes de su escenario
fuente = (RAIZ / "src" / "colibri_bebe.py").read_text(encoding="utf-8")
g = {"__file__": str(RAIZ / "src" / "colibri_bebe.py"), "__name__": "personaje"}
exec(compile(fuente.split("# --- escenario")[0], "colibri_bebe.py", "exec"), g)
esc, col, mat, esfera, cono, pj = g["esc"], g["col"], g["mat"], g["esfera"], g["cono"], g["pj"]


def importar(ident, ancho=None, alto=None, pos=(0, 0, 0), rot_z=0.0):
    """Importa un glTF de Poly Haven, lo agrupa bajo un vacío y lo escala a `ancho` (X/Y) o `alto` (Z)."""
    f = next((PH / ident).glob("*.gltf"))
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(f))
    nuevos = [o for o in bpy.data.objects if o not in antes]
    raiz = bpy.data.objects.new(ident, None); col.objects.link(raiz)
    for o in nuevos:
        if o.parent is None: o.parent = raiz
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in nuevos if o.type == "MESH" for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
    tam = mx - mn
    s = (ancho / max(tam.x, tam.y)) if ancho else (alto / tam.z if alto else 1.0)
    raiz.scale = (s, s, s); raiz.rotation_euler.z = rot_z
    centro = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    raiz.location = Vector(pos) - centro * s
    return raiz, tam * s


# --- cielo de amanecer con el sol detrás del personaje (contraluz dorado) ------------------------
hdr = next((PH / "spruit_sunrise").glob("*.hdr"))
img = bpy.data.images.load(str(hdr))
W, Hh = img.size
px = np.empty(W * Hh * 4, dtype=np.float32); img.pixels.foreach_get(px)
lum = px.reshape(Hh, W, 4)[..., :3].sum(axis=2)
fila, colu = np.unravel_index(np.argmax(lum), lum.shape)
u, v = (colu + 0.5) / W, (fila + 0.5) / Hh            # v desde abajo (pixeles de Blender empiezan abajo)
az_sol = (u - 0.5) * 2 * math.pi                      # atan2(y, -x) en la convención equirectangular de Blender
el_sol = (v - 0.5) * math.pi
deseado = math.atan2(1.0, -0.45)                      # dirección (x=0.45, y=1): detrás y a la derecha del pájaro
w = bpy.data.worlds.new("amanecer"); esc.world = w; w.use_nodes = True
nt = w.node_tree; bg = nt.nodes["Background"]; bg.inputs["Strength"].default_value = 1.1
tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); env = nt.nodes.new("ShaderNodeTexEnvironment")
env.image = img; mp.inputs["Rotation"].default_value[2] = -(deseado - az_sol)
nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
nt.links.new(env.outputs["Color"], bg.inputs["Color"])
d_sol = Vector((0.45, 1.0, 0)).normalized(); d_sol.z = math.tan(max(el_sol, math.radians(6))); d_sol.normalize()
print(f"sol en u={u:.3f} v={v:.3f} elev={math.degrees(el_sol):.1f}°")

sol = bpy.data.lights.new("sol", "SUN"); sol.energy = 4.5; sol.color = (1.0, 0.72, 0.42); sol.angle = math.radians(3)
so = bpy.data.objects.new("sol", sol); col.objects.link(so)
so.rotation_euler = (-d_sol).to_track_quat("-Z", "Y").to_euler()

# --- tronco con musgo donde está parado el colibrí ------------------------------------------------
tronco, tam_t = importar("dead_tree_trunk_02", ancho=4.2, pos=(0.3, 0.2, -0.75), rot_z=math.radians(8))
bpy.context.view_layer.update()
# subir/bajar el pájaro hasta la superficie del tronco bajo sus patas
from mathutils.bvhtree import BVHTree
dg = bpy.context.evaluated_depsgraph_get()
altura = None
for o in [o for o in bpy.data.objects if o.type == "MESH" and o.parent and (o.parent == tronco or o.parent.parent == tronco)]:
    ev = o.evaluated_get(dg); bvh = BVHTree.FromObject(ev, dg)
    inv = o.matrix_world.inverted()
    hit = bvh.ray_cast(inv @ Vector((0.05, 0, 5)), (inv.to_3x3() @ Vector((0, 0, -1))).normalized())
    if hit[0] is not None:
        z = (o.matrix_world @ hit[0]).z
        altura = z if altura is None else max(altura, z)
pj.location.z = (altura if altura is not None else 0.0) + 0.16
print("tronco bajo las patas en z =", altura)

# --- selva tupida: cada planta se importa una vez y se repite como instancia ----------------------
def coleccion_de(ident):
    """Importa el glTF dentro de una colección oculta (para instanciarla muchas veces sin copiar la malla)."""
    c = bpy.data.collections.new(f"ph_{ident}"); esc.collection.children.link(c)
    capa = bpy.context.view_layer.layer_collection.children[c.name]; bpy.context.view_layer.active_layer_collection = capa
    f = next((PH / ident).glob("*.gltf")); bpy.ops.import_scene.gltf(filepath=str(f))
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(k) for o in c.all_objects if o.type == "MESH" for k in o.bound_box]
    mn = Vector([min(q[i] for q in pts) for i in range(3)]); mx = Vector([max(q[i] for q in pts) for i in range(3)])
    c.instance_offset = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    capa.exclude = True
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection
    return c, mx - mn

PLANTAS = {k: coleccion_de(k) for k in ("fern_02", "anthurium_botany_01", "calathea_orbifolia_01", "pachira_aquatica_01", "shrub_04")}
ARBOLES = {k: coleccion_de(k) for k in ("island_tree_01", "tree_small_02")}

def poner(c_tam, pos, ancho=None, alto=None, rz=0.0):
    c, tam = c_tam
    s = ancho / max(tam.x, tam.y) if ancho else alto / tam.z
    e = bpy.data.objects.new(c.name + "_i", None); e.instance_type = "COLLECTION"; e.instance_collection = c
    e.location = pos; e.scale = (s, s, s); e.rotation_euler.z = rz; col.objects.link(e)

SUELO = -0.9
random.seed(7)
# primer plano: hojas grandes a los lados (desenfocadas, enmarcan)
for k, (x, y, a) in enumerate(((-1.9, -1.9, 1.9), (2.0, -2.1, 1.7), (-2.8, -0.3, 2.8), (2.9, 0.2, 2.6), (-1.0, -2.6, 1.3))):
    poner(PLANTAS[random.choice(["anthurium_botany_01", "calathea_orbifolia_01", "fern_02"])], (x, y, SUELO), ancho=a, rz=random.uniform(0, 6.28))
# plano medio y fondo: muchas plantas
for k in range(70):
    x, y = random.uniform(-9, 9), random.uniform(1.0, 16)
    if abs(x) < 1.2 and y < 2.5: continue
    poner(PLANTAS[random.choice(list(PLANTAS))], (x, y, SUELO), ancho=random.uniform(1.6, 3.6) * (1 + y / 14), rz=random.uniform(0, 6.28))
for k in range(16):
    x, y = random.uniform(-14, 14), random.uniform(7, 26)
    poner(ARBOLES[random.choice(list(ARBOLES))], (x, y, SUELO), alto=random.uniform(7, 13), rz=random.uniform(0, 6.28))

# piso de tierra con hojitas
TIERRA = mat("tierra", (0.06, 0.035, 0.018), rough=0.95)
ntt = TIERRA.node_tree; ruido = ntt.nodes.new("ShaderNodeTexNoise"); ruido.inputs["Scale"].default_value = 6
bump = ntt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.4
mz_ = ntt.nodes.new("ShaderNodeValToRGB"); mz_.color_ramp.elements[0].position = 0.45; mz_.color_ramp.elements[1].position = 0.6
mz_.color_ramp.elements[0].color = (0.06, 0.035, 0.018, 1); mz_.color_ramp.elements[1].color = (0.10, 0.22, 0.04, 1)
ntt.links.new(ruido.outputs["Fac"], mz_.inputs["Fac"]); ntt.links.new(mz_.outputs["Color"], ntt.nodes["Principled BSDF"].inputs["Base Color"])
ntt.links.new(ruido.outputs["Fac"], bump.inputs["Height"]); ntt.links.new(bump.outputs["Normal"], ntt.nodes["Principled BSDF"].inputs["Normal"])
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 10, -0.9)); bpy.context.object.data.materials.append(TIERRA)

# neblina dorada suave (da los rayos de luz)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 26, 4)); niebla = bpy.context.object; niebla.scale = (50, 40, 12)
mv = bpy.data.materials.new("niebla"); mv.use_nodes = True; nv = mv.node_tree
nv.nodes.remove(nv.nodes["Principled BSDF"]); vol = nv.nodes.new("ShaderNodeVolumePrincipled")
vol.inputs["Density"].default_value = 0.010; vol.inputs["Color"].default_value = (1.0, 0.85, 0.65, 1); vol.inputs["Anisotropy"].default_value = 0.6
nv.links.new(vol.outputs["Volume"], nv.nodes["Material Output"].inputs["Volume"]); niebla.data.materials.append(mv)

# gotitas de rocío en el tronco y hojas cercanas
AGUA = bpy.data.materials.new("rocio"); AGUA.use_nodes = True
pa = AGUA.node_tree.nodes["Principled BSDF"]; pa.inputs["Transmission Weight"].default_value = 1.0; pa.inputs["Roughness"].default_value = 0.0; pa.inputs["IOR"].default_value = 1.33
for k in range(14):
    esfera(f"gota{k}", (random.uniform(-1.6, 1.8), random.uniform(-0.25, 0.15), pj.location.z - 0.14 + random.uniform(-0.02, 0.03)),
           random.uniform(0.018, 0.04), (1, 1, 0.8), AGUA, seg=16)

# --- luz suave sobre el personaje (relleno cálido al frente + contraluz dorado) -------------------
def luz(nombre, pos, energia, color, tam, mira):
    d = bpy.data.lights.new(nombre, "AREA"); d.energy = energia; d.color = color; d.size = tam
    o = bpy.data.objects.new(nombre, d); col.objects.link(o); o.location = pos
    o.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
z0 = pj.location.z
luz("relleno", (1.5, -4.0, z0 + 2.0), 220, (1.0, 0.86, 0.70), 3.0, (0, 0, z0 + 0.7))
luz("contra", (1.2, 3.0, z0 + 2.2), 600, (1.0, 0.70, 0.40), 1.5, (0, 0, z0 + 0.8))

# --- cámara baja, desenfoque fuerte ----------------------------------------------------------------
cd = bpy.data.cameras.new("cam"); cd.lens = 50; cd.dof.use_dof = True; cd.dof.aperture_fstop = 1.4
cam = bpy.data.objects.new("cam", cd); col.objects.link(cam); esc.camera = cam
objetivo = Vector((0.2, 0, z0 + 0.75))
cam.location = (0.1, -4.6, z0 + 0.45)
cam.rotation_euler = (objetivo - cam.location).to_track_quat("-Z", "Y").to_euler()
cd.dof.focus_distance = (objetivo - cam.location).length

# --- render ----------------------------------------------------------------------------------------
esc.render.engine = "CYCLES"; esc.render.resolution_x, esc.render.resolution_y = 1080, 1920
esc.cycles.samples = MUESTRAS; esc.cycles.use_denoising = True; esc.cycles.volume_bounces = 1
pr = bpy.context.preferences.addons["cycles"].preferences
for tipo in ("OPTIX", "CUDA"):
    try:
        pr.compute_device_type = tipo; pr.get_devices()
        if any(d.type == tipo for d in pr.devices): break
    except TypeError:
        continue
for d in pr.devices: d.use = True
esc.cycles.device = "GPU"
esc.view_settings.view_transform = "AgX"; esc.view_settings.look = "AgX - Medium High Contrast"
esc.render.filepath = SALIDA
pathlib.Path(SALIDA).parent.mkdir(parents=True, exist_ok=True)
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(pathlib.Path(SALIDA).with_suffix(".blend")))
print("LISTO", SALIDA)
