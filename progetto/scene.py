# Costruisce tutta la scena 3D in Blender da zero e la salva in scene.blend.
# Uso: blender -b --factory-startup -P scene.py            (solo costruzione)
#      blender -b scene.blend -P render.py -- <da> <a>     (render dei fotogrammi)
import bpy, math, os, sys
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timeline import FPS, DURATA, TASTI, HOPS, ENTRATA, PANNELLI, SALTO_FINALE, TITOLO

DIR = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(DIR, "tex")
FONTS = ["/usr/share/fonts/truetype/lato/Lato-Black.ttf", "/Library/Fonts/Arial Black.ttf", "C:/Windows/Fonts/ariblk.ttf"]
FONT = next((f for f in FONTS if os.path.exists(f)), None)  # nessuno: font di Blender
BLU = (0.023, 0.06, 0.68, 1)        # #2a47d6 in lineare
BLU_LUCE = (0.16, 0.24, 1.0, 1)     # #6f86ff acceso
N = int(DURATA * FPS)

bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
sc.frame_start, sc.frame_end = 1, N
sc.render.fps = FPS

def F(t):  # secondi -> fotogramma
    return 1 + t * FPS

def px(x, y):  # px dell'interfaccia (2400x1500) -> metri nella scena
    return x / 1000 - 1.2, 0.75 - y / 1000

def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)

# ---------- materiali ----------
def nuovo_mat(nome):
    m = bpy.data.materials.new(nome)
    try:
        m.use_nodes = True  # in Blender 5 è sempre attivo
    except Exception:
        pass
    return m

def sock(lista, nome, tipo):
    return next(s for s in lista if s.name == nome and s.type == tipo)

def mat_base(nome, colore, rough=0.4, coat=0.0, emis=None, forza=0.0):
    m = nuovo_mat(nome)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = colore
    b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = coat
    if emis:
        b.inputs["Emission Color"].default_value = emis
        b.inputs["Emission Strength"].default_value = forza
    return m

def mat_immagine(nome, file, forza=0.8, trasparente_fac=None):
    m = nuovo_mat(nome)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(os.path.join(TEX, file))
    nt.links.new(img.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(img.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = forza
    b.inputs["Roughness"].default_value = 0.55
    b.inputs["Specular IOR Level"].default_value = 0.25  # riflessi leggeri: l'interfaccia deve leggersi
    if trasparente_fac is not None:  # pannello che si accende: mix trasparente -> immagine
        out = nt.nodes["Material Output"]
        mix = nt.nodes.new("ShaderNodeMixShader")
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        nt.links.new(tr.outputs[0], mix.inputs[1])
        nt.links.new(b.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
        mix.inputs[0].default_value = trasparente_fac
        return m, mix
    return m

def piano(nome, w, h, loc, mat):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    o = bpy.context.object
    o.name = nome
    o.scale = (w, h, 1)
    o.data.materials.append(mat)
    return o

def scatola(nome, dim, loc, mat, bevel=0.004):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = nome
    o.scale = dim
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    md = o.modifiers.new("bevel", "BEVEL")
    md.width, md.segments = bevel, 4
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o

def testo(nome, body, size, loc, mat, extrude=0.004):
    cu = bpy.data.curves.new(nome, "FONT")
    cu.body = body
    if FONT:
        cu.font = bpy.data.fonts.load(FONT)
    cu.size = size
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    cu.extrude, cu.bevel_depth, cu.bevel_resolution = extrude, 0.0012, 3
    o = bpy.data.objects.new(nome, cu)
    sc.collection.objects.link(o)
    o.location = loc
    o.data.materials.append(mat)
    return o

# ---------- interfaccia (spenta) + pannelli che si accendono ----------
piano("interfaccia", 2.4, 1.5, (0, 0, 0), mat_immagine("ui_off", "ui_off.png", 4.0))
PAN = {"progetto": (20, 170, 500, 730), "anteprima": (540, 170, 1320, 730),
       "effetti": (1880, 170, 500, 730), "timeline": (20, 920, 2360, 560)}
for (nome, (x, y, w, h)), t in zip(PAN.items(), PANNELLI):
    m, mix = mat_immagine("p_" + nome, f"p_{nome}.png", 4.0, trasparente_fac=0.0)
    cx, cy = px(x + w / 2, y + h / 2)
    piano("pannello_" + nome, w / 1000, h / 1000, (cx, cy, 0.0006), m)
    for tt, v in ((t - 0.01, 0.0), (t + 0.06, 0.7), (t + 0.10, 0.25), (t + 0.18, 1.0)):  # piccolo sfarfallio
        mix.inputs[0].default_value = v
        mix.inputs[0].keyframe_insert("default_value", frame=F(tt))

# ---------- tasti 3D con icona ----------
KEY_TOP = 0.03
tasti = {}
for i, nome in enumerate(TASTI):
    x, y = px(600 + 150 * i, 105)
    k = scatola("tasto_" + nome, (0.112, 0.058, KEY_TOP), (x, y, KEY_TOP / 2),
                mat_base("tasto", (0.012, 0.013, 0.02, 1), rough=0.35, coat=0.3), bevel=0.006)
    ic = nuovo_mat("icona_" + nome)
    nt = ic.node_tree
    b = nt.nodes["Principled BSDF"]
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(os.path.join(TEX, f"i_{nome}.png"))
    mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = "RGBA"
    sock(mixc.inputs, "A", "RGBA").default_value = (0.12, 0.13, 0.17, 1)
    sock(mixc.inputs, "B", "RGBA").default_value = BLU_LUCE
    nt.links.new(sock(mixc.outputs, "Result", "RGBA"), b.inputs["Emission Color"])
    b.inputs["Base Color"].default_value = (0, 0, 0, 1)
    b.inputs["Emission Strength"].default_value = 6.0
    nt.links.new(img.outputs["Alpha"], b.inputs["Alpha"])
    p = piano("icona_" + nome, 0.04, 0.04, (0, 0, KEY_TOP / 2 + 0.0004), ic)
    p.parent = k
    p.location = (0, 0, KEY_TOP / 2 + 0.0004)
    tasti[nome] = (k, mixc, Vector((x, y, KEY_TOP)))

def premi(nome, t):  # il tasto scende e l'icona si accende e resta accesa
    k, mixc, _ = tasti[nome]
    z0 = KEY_TOP / 2
    for tt, z in ((t - 0.01, z0), (t + 0.05, z0 - 0.009), (t + 0.22, z0)):
        k.location.z = z
        k.keyframe_insert("location", index=2, frame=F(tt))
    for tt, v in ((t - 0.01, 0.0), (t + 0.04, 1.0)):
        fac = sock(mixc.inputs, "Factor", "VALUE")
        fac.default_value = v
        fac.keyframe_insert("default_value", frame=F(tt))

# ---------- robottino blu con la A ----------
plast = mat_base("robottino", BLU, rough=0.28, coat=0.6)
scuro = mat_base("visiera", (0.004, 0.006, 0.02, 1), rough=0.15, coat=1.0)
occhi = mat_base("occhi", (1, 1, 1, 1), emis=(0.8, 0.88, 1, 1), forza=8)
bianco = mat_base("marchio", (1, 1, 1, 1), emis=(1, 1, 1, 1), forza=2.5)
antenna_l = mat_base("antenna", (0.3, 0.4, 1, 1), emis=BLU_LUCE, forza=10)

rad = bpy.data.objects.new("robottino", None)
sc.collection.objects.link(rad)
corpo = bpy.data.objects.new("corpo", None)   # pivot ai piedi per schiacciarlo bene
sc.collection.objects.link(corpo); corpo.parent = rad
parti = [
    scatola("busto", (0.05, 0.04, 0.042), (0, 0, 0.033), plast, 0.008),
    scatola("visiera", (0.04, 0.006, 0.018), (0, -0.0195, 0.04), scuro, 0.004),
    scatola("occhio_s", (0.006, 0.004, 0.009), (-0.009, -0.0225, 0.041), occhi, 0.002),
    scatola("occhio_d", (0.006, 0.004, 0.009), (0.009, -0.0225, 0.041), occhi, 0.002),
    scatola("gamba_s", (0.012, 0.014, 0.014), (-0.013, 0, 0.007), plast, 0.003),
    scatola("gamba_d", (0.012, 0.014, 0.014), (0.013, 0, 0.007), plast, 0.003),
    scatola("braccio_s", (0.008, 0.014, 0.018), (-0.029, 0, 0.03), plast, 0.003),
    scatola("braccio_d", (0.008, 0.014, 0.018), (0.029, 0, 0.03), plast, 0.003),
]
bpy.ops.mesh.primitive_cylinder_add(radius=0.0015, depth=0.014, location=(0, 0, 0.061))
parti.append(bpy.context.object); parti[-1].data.materials.append(scuro)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0045, location=(0, 0, 0.069))
parti.append(bpy.context.object); parti[-1].data.materials.append(antenna_l)
bpy.ops.object.shade_smooth()
a = testo("A", "A", 0.014, (0, -0.0205, 0.0215), bianco, extrude=0.001)
a.rotation_euler = (math.radians(90), 0, 0)
parti.append(a)
for p in parti:
    p.parent = corpo

# ---------- titolo finale ----------
bianco_t = mat_base("titolo", (1, 1, 1, 1), emis=(1, 1, 1, 1), forza=3.0)
blu_t = mat_base("opus", BLU_LUCE, emis=BLU_LUCE, forza=4.0)
tit = bpy.data.objects.new("titolo", None); sc.collection.objects.link(tit)
TX, TY = px(1200, 470)
tit.location = (TX, TY, -0.3)
righe = [testo("t3", "Opus 5.5", 0.022, (0, 0, 0.205), blu_t, 0.003),
         testo("t1", "FATTO CON", 0.05, (0, 0, 0.158), bianco_t, 0.006),
         testo("t2", "CLAUDE", 0.064, (0, 0, 0.1), bianco_t, 0.008)]
for r in righe:
    r.rotation_euler = (math.radians(90), 0, 0)
    r.parent = tit

# ---------- movimento del robottino (calcolato fotogramma per fotogramma) ----------
def pos_tasto(n):
    return tasti[n][2]

ARRIVO = Vector((TX, TY - 0.15, 0.0))
salti = []
prec = "Mano"
for t0, t1, n in HOPS:
    salti.append((t0, t1, pos_tasto(prec), pos_tasto(n), 0.065, n))
    prec = n
salti.append((SALTO_FINALE[0], SALTO_FINALE[1], pos_tasto(prec), ARRIVO, 0.26, None))

def stato(t):
    """posizione, rotazione z, schiacciamento (sz) al tempo t"""
    if t < ENTRATA[1]:
        u = max(0.0, (t - ENTRATA[0]) / (ENTRATA[1] - ENTRATA[0]))
        p = pos_tasto("Mano").copy(); p.z += 0.35 * (1 - u * u)
        return p, math.radians(25), 1.12 if u > 0 else 1.0
    atterraggi = [ENTRATA[1]] + [s[1] for s in salti]
    for t0, t1, a0, a1, h, _ in salti:
        if t0 <= t < t1:
            u = (t - t0) / (t1 - t0)
            p = a0.lerp(a1, ease(u) * 0.3 + u * 0.7)
            p.z = a0.z + (a1.z - a0.z) * u + 4 * h * u * (1 - u)
            giro = math.radians(360) * ease(u) if h > 0.2 else 0.0
            return p, math.radians(25) + giro, 1.1
    # a terra: dove ha atterrato l'ultima volta
    p = pos_tasto("Mano")
    for t0, t1, a0, a1, h, _ in salti:
        if t >= t1:
            p = a1
    sz = 1.0
    for ta in atterraggi:  # schiacciamento all'atterraggio
        if 0 <= t - ta < 0.16:
            sz = 1 - 0.2 * math.sin(math.pi * (t - ta) / 0.16)
    for t0, *_ in salti:   # caricamento prima del salto
        if 0 <= t0 - t < 0.1:
            sz = 1 - 0.14 * math.sin(math.pi * (t0 - t) / 0.2)
    rz = math.radians(25) if t < SALTO_FINALE[1] else math.radians(25) * max(0, 1 - (t - SALTO_FINALE[1]) / 0.5)
    if t > 10.2 and t < 10.6:  # saltino di festa davanti al titolo
        u = (t - 10.2) / 0.4
        p = p.copy(); p.z += 0.035 * 4 * u * (1 - u)
    return p.copy(), rz, sz

for f in range(1, N + 1):
    t = (f - 1) / FPS
    p, rz, sz = stato(t)
    rad.location = p
    rad.rotation_euler = (0, 0, rz)
    corpo.scale = (1 / math.sqrt(sz), 1 / math.sqrt(sz), sz)
    rad.keyframe_insert("location", frame=f)
    rad.keyframe_insert("rotation_euler", frame=f)
    corpo.keyframe_insert("scale", frame=f)

for t0, t1, a0, a1, h, n in salti:
    if n:
        premi(n, t1)
premi("Mano", ENTRATA[1])

# il titolo sale con un piccolo rimbalzo
for tt, z in ((TITOLO, -0.3), (TITOLO + 0.35, 0.012), (TITOLO + 0.5, -0.004), (TITOLO + 0.62, 0.0)):
    tit.location.z = z
    tit.keyframe_insert("location", index=2, frame=F(tt))

# ---------- camera ----------
cam_d = bpy.data.cameras.new("camera")
cam_d.lens, cam_d.sensor_width = 35, 36
cam_d.dof.use_dof = True
cam_d.dof.aperture_fstop = 3.2
cam = bpy.data.objects.new("camera", cam_d); sc.collection.objects.link(cam)
sc.camera = cam
mira = bpy.data.objects.new("mira", None); sc.collection.objects.link(mira)
fuoco = bpy.data.objects.new("fuoco", None); sc.collection.objects.link(fuoco)
cam_d.dof.focus_object = fuoco
c = cam.constraints.new("TRACK_TO"); c.target = mira
c.track_axis, c.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"

def cam_stato(t, xs):
    """camera e mira: segue il robottino, poi si alza sui pannelli, poi frontale sul titolo"""
    x = xs
    seg = (Vector((x - 0.07, 0.645 - 0.30, 0.19)), Vector((x + 0.015, 0.62, 0.03)))
    alto = (Vector((TX + 0.05, -1.05, 1.05)), Vector((TX + 0.03, 0.02, 0.0)))
    fronte = (Vector((TX, TY - 0.66, 0.2)), Vector((TX, TY, 0.11)))
    vicino = (Vector((TX, TY - 0.56, 0.18)), Vector((TX, TY, 0.11)))
    def mix(a, b, u):
        u = ease(u)
        return a[0].lerp(b[0], u), a[1].lerp(b[1], u)
    if t < 5.9:
        return seg
    if t < 7.9:
        return mix(seg, alto, (t - 5.9) / 1.6)
    if t < 9.4:
        return mix(alto, fronte, (t - 7.9) / 1.5)
    return mix(fronte, vicino, (t - 9.4) / 2.6)

xs = pos_tasto("Mano").x
for f in range(1, N + 1):
    t = (f - 1) / FPS
    p, _, _ = stato(t)
    xs += (p.x - xs) * 0.12  # la camera insegue con un po' di ritardo
    cl, ml = cam_stato(t, xs)
    cam.location, mira.location = cl, ml
    cam.keyframe_insert("location", frame=f)
    mira.keyframe_insert("location", frame=f)
    fuoco.location = p + Vector((0, 0, 0.03)) if t < 9.2 else Vector((TX, TY - 0.06, 0.09))
    fuoco.keyframe_insert("location", frame=f)

# ---------- luci e mondo ----------
def luce(nome, tipo, energia, colore, loc, size=0.3):
    d = bpy.data.lights.new(nome, tipo)
    d.energy, d.color = energia, colore
    if tipo == "AREA":
        d.size = size
    o = bpy.data.objects.new(nome, d); sc.collection.objects.link(o)
    o.location = loc
    tr = o.constraints.new("TRACK_TO"); tr.target = mira
    return o

luce("chiave", "AREA", 60, (1.0, 0.72, 0.45), (-0.7, -0.5, 0.9), 0.6)
luce("controluce", "AREA", 25, (0.45, 0.55, 1.0), (0.5, 1.2, 0.35), 0.4)
luce("riempimento", "AREA", 8, (1.0, 0.85, 0.7), (0.6, -0.8, 0.3), 0.8)
w = bpy.data.worlds.new("mondo"); sc.world = w
w.color = (0.012, 0.008, 0.006)
w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.012, 0.008, 0.006, 1)
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0

# ---------- render ----------
r = sc.render
r.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 64
sc.cycles.adaptive_threshold = 0.03
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 6
r.resolution_x, r.resolution_y, r.resolution_percentage = 1080, 1920, 100
r.use_motion_blur = True
r.motion_blur_shutter = 0.5
r.use_persistent_data = True
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"
r.image_settings.file_format = "PNG"
r.filepath = os.path.join(DIR, "renders", "full", "f_")

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(DIR, "scene.blend"))
print("scena salvata", N, "fotogrammi")
