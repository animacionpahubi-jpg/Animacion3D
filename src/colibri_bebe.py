"""Colibrí bebé en 3D (prueba de estilo v1) — Pahubi Animación 3D.
Arma el personaje con formas simples (estilo juguete/película animada) a partir de la hoja 2D
(ANIMACION-2D/assets/kit/bebe-con-gorro.jpg) y renderiza una imagen vertical 1080x1920.
Uso:  blender -b -P src/colibri_bebe.py -- [salida.png] [muestras]
"""
import bpy, math, sys, pathlib
from mathutils import Vector, Euler

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RAIZ = pathlib.Path(__file__).resolve().parents[1]
SALIDA = args[0] if args else str(RAIZ / "pruebas" / "colibri-bebe-v1.png")
MUESTRAS = int(args[1]) if len(args) > 1 and args[1].isdigit() else 160

# --- escena limpia --------------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
esc = bpy.context.scene
col = esc.collection


def mat(nombre, color, rough=0.6, sheen=0.0, sss=0.0, coat=0.0, emis=0.0):
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    if sheen: p.inputs["Sheen Weight"].default_value = sheen; p.inputs["Sheen Tint"].default_value = (1, 1, 0.9, 1)
    if sss: p.inputs["Subsurface Weight"].default_value = sss; p.inputs["Subsurface Radius"].default_value = (0.3, 0.2, 0.1)
    if coat: p.inputs["Coat Weight"].default_value = coat
    if emis: p.inputs["Emission Color"].default_value = (*color, 1); p.inputs["Emission Strength"].default_value = emis
    return m


def rayas(nombre, c1, c2, escala=4.0, rot=(0, 0, 0)):
    """Material de gorro tejido: franjas diagonales (onda en coordenadas del objeto)."""
    m = mat(nombre, c1, rough=0.85, sheen=0.6)
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = rot
    w = nt.nodes.new("ShaderNodeTexWave"); w.inputs["Scale"].default_value = escala; w.inputs["Distortion"].default_value = 0.4
    w.bands_direction = "Z"
    r = nt.nodes.new("ShaderNodeValToRGB"); r.color_ramp.elements[0].position = 0.45; r.color_ramp.elements[1].position = 0.55
    r.color_ramp.elements[0].color = (*c1, 1); r.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], w.inputs["Vector"])
    nt.links.new(w.outputs["Fac"], r.inputs["Fac"]); nt.links.new(r.outputs["Color"], p.inputs["Base Color"])
    return m


def esfera(nombre, pos, radio, escala=(1, 1, 1), m=None, rot=(0, 0, 0), padre=None, seg=48):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=radio, location=pos, rotation=rot)
    o = bpy.context.object; o.name = nombre; o.scale = escala
    bpy.ops.object.shade_smooth()
    if m: o.data.materials.append(m)
    if padre: o.parent = padre
    return o


def cono(nombre, base, punta, r1, r2, m, padre=None):
    base, punta = Vector(base), Vector(punta); d = punta - base
    bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=r1, radius2=r2, depth=d.length, location=(base + punta) / 2)
    o = bpy.context.object; o.name = nombre
    o.rotation_mode = "QUATERNION"; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    bpy.ops.object.shade_smooth(); o.data.materials.append(m)
    if padre: o.parent = padre
    return o


# --- materiales -----------------------------------------------------------------------------------
VERDE = mat("plumas", (0.16, 0.50, 0.04), rough=0.75, sheen=1.0, sss=0.08)
PANZA = mat("panza", (0.55, 0.70, 0.22), rough=0.8, sheen=0.8)
PICO = mat("pico", (0.10, 0.10, 0.45), rough=0.35, coat=0.6)
BLANCO = mat("ojo", (0.97, 0.97, 0.97), rough=0.15, coat=1.0)
IRIS = mat("iris", (0.30, 0.08, 0.60), rough=0.2, coat=1.0)
PUPILA = mat("pupila", (0.03, 0.02, 0.06), rough=0.1, coat=1.0)
BRILLO = mat("brillo", (1, 1, 1), emis=6.0)
CACHETE = mat("cachete", (0.95, 0.18, 0.06), rough=0.7, sss=0.3)
GORRO = rayas("gorro", (0.25, 0.07, 0.45), (0.55, 0.32, 0.78), escala=3.2, rot=(0.0, 0.6, 0.3))
POMPON = mat("pompon", (0.45, 0.22, 0.70), rough=0.9, sheen=1.0)
ALA = mat("ala", (0.95, 0.45, 0.52), rough=0.5, sss=0.4)
COLA = mat("cola", (0.70, 0.40, 0.82), rough=0.5, sss=0.4)
PATA = mat("pata", (0.22, 0.10, 0.50), rough=0.4)
HOJA = mat("cresta", (0.45, 0.80, 0.20), rough=0.6, sss=0.2)

# panza crema: degradé en el mismo material (frente y abajo), así el plumón también toma el color
nt = VERDE.node_tree; pr_ = nt.nodes["Principled BSDF"]
tc_ = nt.nodes.new("ShaderNodeTexCoord"); sx = nt.nodes.new("ShaderNodeSeparateXYZ")
mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.22; mr.inputs["From Max"].default_value = 0.52
mz = nt.nodes.new("ShaderNodeMapRange"); mz.inputs["From Min"].default_value = 0.70; mz.inputs["From Max"].default_value = 0.45
mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
mix.inputs["A"].default_value = (0.16, 0.50, 0.04, 1); mix.inputs["B"].default_value = (0.62, 0.78, 0.30, 1)
nt.links.new(tc_.outputs["Object"], sx.inputs["Vector"]); nt.links.new(sx.outputs["X"], mr.inputs["Value"]); nt.links.new(sx.outputs["Z"], mz.inputs["Value"])
nt.links.new(mr.outputs["Result"], mul.inputs[0]); nt.links.new(mz.outputs["Result"], mul.inputs[1])
nt.links.new(mul.outputs["Value"], mix.inputs["Factor"]); nt.links.new(mix.outputs["Result"], pr_.inputs["Base Color"])

# --- personaje (local: frente +X, izquierda +Y, arriba +Z) ----------------------------------------
pj = bpy.data.objects.new("colibri_bebe", None); col.objects.link(pj)

# cuerpo + cabeza como una sola forma blanda (metabolas)
mb = bpy.data.metaballs.new("cuerpo_mb"); mb.resolution = 0.03; mb.render_resolution = 0.015
for pos, r in (((0, 0, 0.46), 0.63), ((0.05, 0, 1.08), 0.62)):
    e = mb.elements.new(); e.co = pos; e.radius = r; e.stiffness = 1.7
mbo = bpy.data.objects.new("cuerpo_mb", mb); col.objects.link(mbo)
bpy.context.view_layer.objects.active = mbo; mbo.select_set(True)
bpy.ops.object.convert(target="MESH"); cuerpo = bpy.context.object; cuerpo.name = "cuerpo"
from mathutils import Matrix
cuerpo.data.transform(Matrix.Diagonal((1.06, 1.06, 0.80, 1)))   # más bajito y redondo, como el dibujo
bpy.ops.object.shade_smooth(); cuerpo.data.materials.append(VERDE); cuerpo.parent = pj

H = Vector((0.05, 0, 0.87)); RH = 0.52   # centro y radio aprox. de la cabeza

# plumón: pelitos cortos (sistema de partículas de pelo)
try:
    ps = cuerpo.modifiers.new("plumon", "PARTICLE_SYSTEM").particle_system.settings
    ps.type = "HAIR"; ps.count = 9000; ps.hair_length = 0.045; ps.use_advanced_hair = True
    ps.root_radius = 0.004; ps.tip_radius = 0.0; ps.radius_scale = 1.0
    ps.child_type = "INTERPOLATED"; ps.child_percent = 6; ps.rendered_child_count = 6
    ps.roughness_2 = 0.03; ps.material_slot = "plumas"
except Exception as ex:
    print("sin plumón:", ex)

# panza crema


def en_cabeza(az, el, d=1.0):
    a, e = math.radians(az), math.radians(el)
    return H + Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e))) * RH * d


# ojos grandes
for lado in (1, -1):
    n = (en_cabeza(32 * lado, 12) - H).normalized()
    c = en_cabeza(32 * lado, 10, 0.86)
    rot = Vector((1, 0, 0)).rotation_difference(n).to_euler()
    esfera(f"ojo{lado}", c, 0.15, (0.55, 1, 1.12), BLANCO, rot=rot, padre=pj)
    esfera(f"iris{lado}", c + n * 0.05 + Vector((0, 0, -0.01)), 0.095, (0.45, 1, 1.1), IRIS, rot=rot, padre=pj)
    esfera(f"pupila{lado}", c + n * 0.085 + Vector((0, 0, -0.012)), 0.05, (0.4, 1, 1.1), PUPILA, rot=rot, padre=pj)
    esfera(f"brillo{lado}", c + n * 0.10 + Vector((0, 0.02 * lado, 0.035)), 0.02, m=BRILLO, padre=pj, seg=16)
    esfera(f"cachete{lado}", en_cabeza(44 * lado, -22, 0.90), 0.07, (0.3, 1, 0.8), CACHETE,
           rot=Vector((1, 0, 0)).rotation_difference((en_cabeza(48 * lado, -18) - H).normalized()).to_euler(), padre=pj)

# pico largo, un poquito hacia abajo
cono("pico", H + Vector((0.34, 0, -0.06)), H + Vector((1.08, 0, -0.20)), 0.075, 0.006, PICO, padre=pj)

# gorro tejido inclinado hacia atrás + borde + pompón
g = esfera("gorro", H + Vector((-0.14, 0, 0.27)), 0.40, (1.0, 1.05, 0.74), GORRO, rot=(0, math.radians(-32), 0), padre=pj)
bpy.ops.mesh.primitive_torus_add(major_radius=0.37, minor_radius=0.06, location=H + Vector((-0.07, 0, 0.17)),
                                 rotation=(0, math.radians(-32), 0))
borde = bpy.context.object; borde.name = "borde"; borde.scale = (1.0, 1.05, 1.0); bpy.ops.object.shade_smooth()
borde.data.materials.append(GORRO); borde.parent = pj
esfera("pompon", H + Vector((-0.40, 0, 0.55)), 0.10, m=POMPON, padre=pj)

# cresta de hojita
esfera("cresta", H + Vector((0.12, 0, 0.48)), 0.09, (0.35, 0.18, 1.0), HOJA, rot=(0, math.radians(22), 0), padre=pj)
esfera("cresta2", H + Vector((0.22, 0, 0.44)), 0.06, (0.3, 0.15, 0.9), HOJA, rot=(0, math.radians(45), 0), padre=pj)

# alas rosadas pegadas al cuerpo y cola
def pluma(nombre, raiz, largo, ancho, ang_y, ang_z, m, ang_x=0.0):
    """Pluma: elipsoide alargado que nace en `raiz` y apunta según los ángulos (grados)."""
    rot = Euler((math.radians(ang_x), math.radians(ang_y), math.radians(ang_z)))
    d = Vector((1, 0, 0)); d.rotate(rot)
    return esfera(nombre, Vector(raiz) + d * largo, largo, (1.0, ancho, 0.07 / largo * 0.6 + 0.0), m, rot=rot, padre=pj)

# alas: abanico de 4 plumas por lado, pegadas al costado y hacia atrás/abajo
for lado in (1, -1):
    for i, (ay, l) in enumerate(((115, 0.26), (130, 0.30), (145, 0.30), (160, 0.26))):
        pluma(f"ala{lado}{i}", (0.02, 0.50 * lado, 0.52), l, 0.30, ay, 18 * lado, ALA if i < 2 else COLA, ang_x=90)
# cola: abanico hacia atrás y abajo
for i, az in enumerate((-22, -8, 8, 22)):
    pluma(f"cola{i}", (-0.50, 0.0, 0.22), 0.24, 0.32, 140, 180 + az, COLA, ang_x=90)

# patitas
for lado in (1, -1):
    y = 0.14 * lado
    cono(f"pierna{lado}", (0.02, y, 0.18), (0.05, y, -0.02), 0.03, 0.025, PATA, padre=pj)
    for dz in (-25, 0, 25):
        a = math.radians(dz)
        cono(f"dedo{lado}{dz}", (0.05, y, -0.02), (0.05 + 0.14 * math.cos(a), y + 0.14 * math.sin(a), -0.04), 0.022, 0.012, PATA, padre=pj)

pj.location = (0, 0, 0.04)
pj.rotation_euler = (0, 0, math.radians(-38))   # 3/4 hacia la cámara, pico a la derecha

# --- escenario: rama con hojas y flor, fondo desenfocado ------------------------------------------
MADERA = mat("rama", (0.30, 0.17, 0.08), rough=0.9)
HOJAS = mat("hojas", (0.22, 0.55, 0.12), rough=0.55, sss=0.2)
FLOR = mat("flor", (0.98, 0.45, 0.65), rough=0.5, sss=0.4)
cono("rama", (-2.2, 0.3, -0.12), (2.4, -0.1, -0.06), 0.13, 0.08, MADERA)
for x, y, rz in ((-1.3, 0.35, 40), (1.5, -0.2, -30), (1.0, 0.25, 70)):
    esfera(f"hoja{x}", (x, y, 0.02), 0.32, (1.0, 0.45, 0.06), HOJAS, rot=(0.2, -0.15, math.radians(rz)))
for i in range(5):
    a = i * 2 * math.pi / 5
    esfera(f"petalo{i}", (1.3 + 0.13 * math.cos(a), -0.35, 0.22 + 0.13 * math.sin(a)), 0.11, (1, 0.35, 0.7), FLOR, rot=(math.pi / 2, 0, -a))
esfera("centro_flor", (1.3, -0.38, 0.22), 0.06, m=mat("polen", (1.0, 0.8, 0.2)))

# fondo: pradera con colinas, árboles redonditos y flores (queda desenfocada por la cámara)
import random
random.seed(4)
PASTO = mat("pasto", (0.20, 0.50, 0.08), rough=0.9, sheen=0.5)
PASTO2 = mat("pasto2", (0.30, 0.62, 0.12), rough=0.9, sheen=0.5)
TRONCO = mat("tronco", (0.28, 0.16, 0.08), rough=0.9)
COPAS = [mat(f"copa{k}", c, rough=0.8, sheen=0.6) for k, c in enumerate(((0.14, 0.42, 0.08), (0.22, 0.52, 0.10), (0.30, 0.58, 0.14)))]
FLORES = [mat(f"flor{k}", c, rough=0.5) for k, c in enumerate(((0.98, 0.45, 0.65), (1.0, 0.85, 0.25), (0.95, 0.95, 0.95), (0.70, 0.45, 0.95)))]
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 20, -1.6)); bpy.context.object.data.materials.append(PASTO)
for x, y, r, h in ((-9, 26, 9, 0.35), (6, 30, 11, 0.40), (16, 22, 8, 0.35), (-18, 20, 9, 0.30), (0, 40, 16, 0.35)):
    esfera(f"colina{x}", (x, y, -1.6), r, (1, 0.8, h), PASTO2 if x % 2 else PASTO, seg=48)
for k in range(9):
    x, y = random.uniform(-14, 14), random.uniform(13, 28)
    if abs(x) < 2.5: x += 5 * (1 if x >= 0 else -1)
    s = random.uniform(0.8, 1.4)
    cono(f"tronco{k}", (x, y, -1.6), (x, y, 1.2 * s), 0.18 * s, 0.12 * s, TRONCO)
    for j in range(3):
        esfera(f"copa{k}{j}", (x + random.uniform(-0.8, 0.8) * s, y + random.uniform(-0.4, 0.4), (1.6 + random.uniform(0, 1.2)) * s),
               random.uniform(0.9, 1.3) * s, m=random.choice(COPAS), seg=32)
for k in range(140):
    x, y = random.uniform(-9, 9), random.uniform(3, 18)
    esfera(f"florecita{k}", (x, y, -1.55 + random.uniform(0, 0.15)), random.uniform(0.06, 0.12), m=random.choice(FLORES), seg=12)
# hojas cercanas abajo (primer plano desenfocado)
for x, z in ((-0.9, -0.55), (0.2, -0.75), (1.1, -0.6), (-0.3, -0.95)):
    esfera(f"hoja_cerca{x}", (x, -1.6, z), 0.45, (1.0, 0.35, 0.08), HOJAS, rot=(1.2, 0.3, x))
sol = bpy.data.lights.new("sol", "SUN"); sol.energy = 2.5; sol.color = (1.0, 0.92, 0.80); sol.angle = math.radians(8)
so = bpy.data.objects.new("sol", sol); col.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(30))

w = bpy.data.worlds.new("cielo"); esc.world = w; w.use_nodes = True
wn = w.node_tree; bg = wn.nodes["Background"]; bg.inputs["Strength"].default_value = 0.9
tcw = wn.nodes.new("ShaderNodeTexCoord"); sw = wn.nodes.new("ShaderNodeSeparateXYZ"); rw = wn.nodes.new("ShaderNodeValToRGB")
rw.color_ramp.elements[0].position = 0.0; rw.color_ramp.elements[0].color = (0.80, 0.90, 1.0, 1)    # horizonte claro
rw.color_ramp.elements[1].position = 0.45; rw.color_ramp.elements[1].color = (0.25, 0.55, 0.95, 1)  # cielo azul arriba
wn.links.new(tcw.outputs["Generated"], sw.inputs["Vector"]); wn.links.new(sw.outputs["Z"], rw.inputs["Fac"]); wn.links.new(rw.outputs["Color"], bg.inputs["Color"])
# nubecitas lejanas
NUBE = mat("nube", (1, 1, 1), rough=1.0, sheen=1.0, emis=0.4)
for x, z in ((-6, 9), (5, 11), (12, 8)):
    for j in range(4):
        esfera(f"nube{x}{j}", (x + j * 0.9, 34, z + (0.4 if j in (1, 2) else 0)), 1.0 + 0.3 * (j in (1, 2)), m=NUBE, seg=24)

# --- luces -----------------------------------------------------------------------------------------
def luz(nombre, pos, energia, color, tam, mira=(0, 0, 0.8)):
    d = bpy.data.lights.new(nombre, "AREA"); d.energy = energia; d.color = color; d.size = tam
    o = bpy.data.objects.new(nombre, d); col.objects.link(o); o.location = pos
    o.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()

luz("principal", (2.5, -3.5, 3.5), 380, (1.0, 0.93, 0.82), 2.5)
luz("relleno", (-3.0, -3.0, 1.5), 110, (0.8, 0.88, 1.0), 4.0)
luz("contra", (-1.5, 3.0, 3.0), 400, (1.0, 0.95, 0.85), 1.5)

# --- cámara vertical con desenfoque suave ---------------------------------------------------------
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 70; cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 1.6
cam = bpy.data.objects.new("cam", cam_d); col.objects.link(cam); esc.camera = cam
cam.location = (0.25, -6.0, 0.55)
objetivo = Vector((0.22, 0, 0.92))
cam.rotation_euler = (objetivo - cam.location).to_track_quat("-Z", "Y").to_euler()
cam_d.dof.focus_distance = (objetivo - cam.location).length

# --- render ----------------------------------------------------------------------------------------
esc.render.engine = "CYCLES"
esc.render.resolution_x, esc.render.resolution_y = 1080, 1920
esc.cycles.samples = MUESTRAS; esc.cycles.use_denoising = True
try:
    pr = bpy.context.preferences.addons["cycles"].preferences
    for tipo in ("OPTIX", "CUDA"):
        try:
            pr.compute_device_type = tipo; pr.get_devices()
            if any(d.type == tipo for d in pr.devices): break
        except TypeError:
            continue
    for d in pr.devices: d.use = True
    esc.cycles.device = "GPU"
except Exception as ex:
    print("render en CPU:", ex)
esc.view_settings.view_transform = "Standard"; esc.view_settings.look = "None"
esc.render.filepath = SALIDA
pathlib.Path(SALIDA).parent.mkdir(parents=True, exist_ok=True)
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(pathlib.Path(SALIDA).with_suffix(".blend")))
print("LISTO", SALIDA)
