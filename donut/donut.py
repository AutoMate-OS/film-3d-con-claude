# Il donut di Blender, scritto tutto in codice (Claude, 24/10/2026). Nessuna finestra di Blender aperta.
# Costruisce la scena: piatto, ciambella che cresce, glassa che cola, zuccherini che cadono uno per uno, luce calda da studio.
# Uso:  blender -b -P donut.py -- [salva scene.blend]
import bpy, bmesh, math, random, sys
from mathutils import Vector, Matrix

GLASSA = "cioccolato"
ZUCCHERINI = 140

COLORI_GLASSA = {"cioccolato": (0.055, 0.022, 0.011), "pistacchio": (0.42, 0.56, 0.17), "fragola": (0.80, 0.22, 0.32), "vaniglia": (0.85, 0.74, 0.55)}
COLORI_ZUCCHERINI = [(0.03, 0.08, 0.68), (0.20, 0.04, 0.70), (0.95, 0.30, 0.45), (0.98, 0.78, 0.10), (0.92, 0.92, 0.90), (0.05, 0.55, 0.30)]
FPS = 30
T = {"piatto": 1, "ciambella": 24, "glassa": 54, "glassa_fine": 120, "zuccherini": 126, "zuccherini_fine": 186, "fine": 360}
random.seed(7)

# --- scena pulita ---------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps, sc.frame_start, sc.frame_end = FPS, 1, T["fine"]
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920


def materiale(nome, colore, rugosita=0.5, coat=0.0, sss=0.0, rumore=None):
    m = bpy.data.materials.new(nome); m.use_nodes = True
    n = m.node_tree.nodes; p = n["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*colore, 1)
    p.inputs["Roughness"].default_value = rugosita
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Subsurface Weight"].default_value = sss
    if rumore:  # leggera variazione di colore (impasto, glassa non piatta)
        tx = n.new("ShaderNodeTexNoise"); tx.inputs["Scale"].default_value = rumore[0]
        rp = n.new("ShaderNodeValToRGB")
        rp.color_ramp.elements[0].color = (*[c * rumore[1] for c in colore], 1)
        rp.color_ramp.elements[1].color = (*[min(1, c * rumore[2]) for c in colore], 1)
        m.node_tree.links.new(tx.outputs["Fac"], rp.inputs["Fac"])
        m.node_tree.links.new(rp.outputs["Color"], p.inputs["Base Color"])
    return m


def liscio(o, livelli=2):
    o.modifiers.new("liscio", "SUBSURF").levels = livelli
    o.modifiers["liscio"].render_levels = livelli
    for f in o.data.polygons: f.use_smooth = True


# --- piatto e fondo ---------------------------------------------------------------
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=1.85, depth=0.07, location=(0, 0, -0.5))
piatto = bpy.context.object; piatto.name = "piatto"
bv = piatto.modifiers.new("bordo", "BEVEL"); bv.width, bv.segments = 0.03, 4
for f in piatto.data.polygons: f.use_smooth = True
piatto.data.materials.append(materiale("ceramica", (0.86, 0.87, 0.9), 0.22, coat=0.4))

bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.54))
pav = bpy.context.object; pav.name = "fondo"
pav.data.materials.append(materiale("fondo", (0.80, 0.84, 0.95), 0.9))   # azzurro chiaro del look CHIARO

# --- ciambella (impasto) ------------------------------------------------------------
bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.42, major_segments=128, minor_segments=64)
ciambella = bpy.context.object; ciambella.name = "ciambella"
for v in ciambella.data.vertices:          # schiacciata sotto come una ciambella vera
    if v.co.z < 0: v.co.z *= 0.72
tex = bpy.data.textures.new("impasto", "CLOUDS"); tex.noise_scale = 0.35
d = ciambella.modifiers.new("irregolare", "DISPLACE"); d.texture, d.strength = tex, 0.035
liscio(ciambella)
ciambella.data.materials.append(materiale("impasto", (0.50, 0.24, 0.07), 0.6, sss=0.06, rumore=(9, 0.7, 1.35)))

# --- glassa: costruita sulla forma del toro, colonna per colonna (bordo liscio), con le gocce che colano ----
R, r = 1.0, 0.42 + 0.03          # raggio della glassa appena sopra l'impasto
gocce = [(2 * math.pi * k / 9 + random.uniform(-0.25, 0.25), random.uniform(0.22, 0.5), random.uniform(0.06, 0.12)) for k in range(9)]
def goccia(u, esterno):              # quanto scende la glassa in quel punto (radianti sul toro)
    g = 0.0
    for c, prof, larg in gocce:
        du = math.atan2(math.sin(u - c), math.cos(u - c))
        g += prof * math.exp(-(du / larg) ** 2)
    return g if esterno else g * 0.35
def punto(u, v):
    x = (R + r * math.cos(v)) * math.cos(u); y = (R + r * math.cos(v)) * math.sin(u); z = r * math.sin(v)
    return (x, y, z * 0.72 if z < 0 else z)
NU, NV = 256, 40
def griglia(f):                      # f = quanto è colata (0 = solo una striscia in cima, 1 = finita)
    pts = []
    for i in range(NU):
        u = 2 * math.pi * i / NU
        v_est = 0.12 - goccia(u, True); v_int = math.pi - 0.15 + goccia(u, False)
        lag = goccia(u, True) / 0.5          # le gocce arrivano per ultime
        fe = max(0.0, min(1.0, (f * (1 + 0.6) - 0.6 * lag) / 1.0)) if f < 1 else 1.0
        fe = 1 - (1 - fe) ** 2
        top = math.pi / 2
        a0 = top - (top - v_est) * max(0.05, fe); a1 = top + (v_int - top) * max(0.05, fe)
        for j in range(NV):
            pts.append(punto(u, a0 + (a1 - a0) * j / (NV - 1)))
    return pts
facce = [(i * NV + j, ((i + 1) % NU) * NV + j, ((i + 1) % NU) * NV + j + 1, i * NV + j + 1) for i in range(NU) for j in range(NV - 1)]
me = bpy.data.meshes.new("glassa"); me.from_pydata(griglia(1.0), [], facce); me.update()
glassa = bpy.data.objects.new("glassa", me); sc.collection.objects.link(glassa)
glassa.shape_key_add(name="striscia", from_mix=False)
passi = [0.0, 0.25, 0.5, 0.75, 1.0]
for k, f in enumerate(passi):
    sk = glassa.shape_key_add(name=f"colata_{k}", from_mix=False)
    for vi, co in enumerate(griglia(f)): sk.data[vi].co = co
glassa.data.shape_keys.use_relative = False
glassa.data.shape_keys.key_blocks[0].data.foreach_set("co", [c for p in griglia(0.0) for c in p])
ks = glassa.data.shape_keys
for fr, val in ((T["glassa"], (1) * 10), (T["glassa_fine"], (len(passi)) * 10)):
    ks.eval_time = val; ks.keyframe_insert("eval_time", frame=fr)
so = glassa.modifiers.new("spessore", "SOLIDIFY"); so.thickness, so.offset = 0.03, 1
liscio(glassa)
glassa.data.materials.append(materiale("glassa", COLORI_GLASSA[GLASSA], 0.16, coat=0.7, rumore=(4, 0.85, 1.15)))

# la ciambella cresce sul piatto (con un piccolo rimbalzo), la glassa le sta attaccata
radice = bpy.data.objects.new("donut", None); sc.collection.objects.link(radice)
for o in (ciambella, glassa): o.parent = radice
for fr, s in ((T["ciambella"], 0.001), (T["ciambella"] + 14, 1.05), (T["ciambella"] + 22, 1.0)):
    radice.scale = (s, s, s); radice.keyframe_insert("scale", frame=fr)

# --- zuccherini ---------------------------------------------------------------------
bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.02, depth=0.1)
base = bpy.context.object; base.name = "zuccherino_base"
liscio(base, 1); base.hide_render = base.hide_viewport = True
mat_z = [materiale(f"zuccherino_{i}", c, 0.35, coat=0.3) for i, c in enumerate(COLORI_ZUCCHERINI)]
deps = bpy.context.evaluated_depsgraph_get()
sc.frame_set(T["fine"])
ge = glassa.evaluated_get(deps); mg = ge.to_mesh()
punti = [(glassa.matrix_world @ p.center, p.normal.copy()) for p in mg.polygons if p.normal.z > 0.6 and p.center.z > 0.3]
ge.to_mesh_clear()
random.shuffle(punti)
for i, (pos, nor) in enumerate(punti[:ZUCCHERINI]):
    z = bpy.data.objects.new(f"zuccherino_{i:03d}", base.data.copy()); sc.collection.objects.link(z)
    z.data.materials.clear(); z.data.materials.append(random.choice(mat_z))
    tang = nor.cross(Vector((random.uniform(-1, 1), random.uniform(-1, 1), 0))).normalized()
    z.matrix_world = Matrix.Translation(pos + nor * 0.012) @ tang.to_track_quat("Z", "Y").to_matrix().to_4x4()
    z.parent = radice; z.matrix_parent_inverse = radice.matrix_world.inverted()
    arrivo = T["zuccherini"] + int(i / max(1, ZUCCHERINI - 1) * (T["zuccherini_fine"] - T["zuccherini"] - 10))
    fine_loc, fine_rot = z.location.copy(), z.rotation_euler.copy()
    z.location = fine_loc + Vector((0, 0, 2.2)); z.rotation_euler = (random.uniform(0, 6), random.uniform(0, 6), 0)
    z.keyframe_insert("location", frame=arrivo - 10); z.keyframe_insert("rotation_euler", frame=arrivo - 10)
    z.location, z.rotation_euler = fine_loc, fine_rot
    z.keyframe_insert("location", frame=arrivo); z.keyframe_insert("rotation_euler", frame=arrivo)
    z.scale = (0, 0, 0); z.keyframe_insert("scale", frame=arrivo - 11)
    z.scale = (1, 1, 1); z.keyframe_insert("scale", frame=arrivo - 10)
sc.frame_set(1)

# giradischi lento: il donut ruota sempre, così nessun fotogramma è fermo
radice.rotation_euler = (0, 0, 0); radice.keyframe_insert("rotation_euler", frame=1)
radice.rotation_euler = (0, 0, math.radians(110)); radice.keyframe_insert("rotation_euler", frame=T["fine"])
for fc in radice.animation_data.action.fcurves if hasattr(radice.animation_data.action, "fcurves") else []:
    if fc.data_path == "rotation_euler":
        for k in fc.keyframe_points: k.interpolation = "LINEAR"

# --- luci da studio calde -------------------------------------------------------------
def luce(nome, loc, energia, colore, dim):
    l = bpy.data.lights.new(nome, "AREA"); l.energy, l.color, l.size = energia, colore, dim
    o = bpy.data.objects.new(nome, l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
luce("chiave", (-3.2, -3.0, 4.2), 1100, (1.0, 0.84, 0.68), 2.2)
luce("contro", (2.8, 3.2, 2.6), 650, (0.85, 0.9, 1.0), 2.0)
luce("riempimento", (4.0, -2.0, 1.4), 90, (1.0, 0.95, 0.9), 4.0)
w = bpy.data.worlds.new("mondo"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.78, 0.82, 0.93, 1)
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45

# --- camere ---------------------------------------------------------------------------
fuoco = bpy.data.objects.new("fuoco", None); sc.collection.objects.link(fuoco); fuoco.location = (0, -0.6, 0.15)
def camera(nome, loc, lente, fstop, mira=(0, 0, 0.0)):
    c = bpy.data.cameras.new(nome); c.lens, c.sensor_fit, c.sensor_width = lente, "HORIZONTAL", 36
    c.dof.use_dof, c.dof.aperture_fstop, c.dof.focus_object = True, fstop, fuoco
    o = bpy.data.objects.new(nome, c); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o
cam_eroe = camera("eroe", (0, -5.6, 3.6), 58, 4.0)
camera("macro", (0.9, -3.1, 0.9), 95, 2.2, mira=(0.3, -0.5, 0.05))
camera("alto", (0, -2.2, 6.0), 50, 5.6)
sc.camera = cam_eroe

# --- render ---------------------------------------------------------------------------
sc.render.engine = "CYCLES"; sc.cycles.samples = 96; sc.cycles.use_denoising = True
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
sc.render.image_settings.file_format = "PNG"

a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if a and a[0] == "salva":
    bpy.ops.wm.save_as_mainfile(filepath=a[1] if len(a) > 1 else "scene.blend")
    print("salvato", GLASSA, ZUCCHERINI, "zuccherini", len(punti), "punti utili")
