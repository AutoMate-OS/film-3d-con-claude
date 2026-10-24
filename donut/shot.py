# Ripresa sulla GPU (Cycles + OptiX): blender -b X.blend -P shot.py -- <nome> <camera> <da> <a> [fil] [campioni]
# Salta i fotogrammi già fatti (VM spot ripartibile). "fil" = geometria essenziale in fil di ferro blu.
import bpy, sys, os, time
a = sys.argv[sys.argv.index("--") + 1:]
nome, cam, da, fino = a[0], a[1], int(a[2]), int(a[3])
fil = "fil" in a[4:]; campioni = next((int(x) for x in a[4:] if x.isdigit()), 96)
sc = bpy.context.scene
pr = bpy.context.preferences.addons["cycles"].preferences
pr.compute_device_type = "OPTIX"; pr.get_devices()
for d in pr.devices: d.use = d.type == "OPTIX"
print("GPU:", [d.name for d in pr.devices if d.use], flush=True)
sc.cycles.device = "GPU"; sc.cycles.samples = campioni; sc.cycles.denoiser = "OPTIX"
sc.camera = bpy.data.objects[cam]
if fil:
    m = bpy.data.materials.new("fil"); m.use_nodes = True; nt = m.node_tree
    wf = nt.nodes.new("ShaderNodeWireframe"); wf.use_pixel_size = True; wf.inputs["Size"].default_value = 2.2
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.16, 0.28, 0.9, 1); em.inputs["Strength"].default_value = 3
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(wf.outputs["Fac"], mx.inputs["Fac"]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    for o in sc.objects:
        if o.type == "MESH" and o.name not in ("fondo", "piatto"): o.hide_render = True
    bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.42, major_segments=40, minor_segments=20)
    t = bpy.context.object; t.data.materials.append(m); t.parent = bpy.data.objects["donut"]
    for v in t.data.vertices:
        if v.co.z < 0: v.co.z *= 0.72
base = os.path.join(os.path.dirname(bpy.data.filepath), "renders", nome); os.makedirs(base, exist_ok=True)
for f in range(da, fino + 1):
    out = os.path.join(base, f"f_{f:04d}.png")
    if os.path.exists(out): continue
    sc.frame_set(f); sc.render.filepath = out
    t0 = time.time(); bpy.ops.render.render(write_still=True)
    print(f"frame {nome} {f}: {time.time() - t0:.2f} s", flush=True)
