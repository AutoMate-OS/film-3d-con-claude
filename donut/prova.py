# Fotogrammi di prova veloci (EEVEE, anche su CPU): blender -b scene.blend -P prova.py -- <percento> <camera>:<fotogramma>[:fil] ...
# Esempio: -- 50 eroe:20 eroe:45 eroe:100 eroe:160 eroe:300 macro:300 eroe:150:fil
import bpy, sys, os, time
a = sys.argv[sys.argv.index("--") + 1:]
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = 32
sc.render.resolution_percentage = int(a[0])
base = os.path.join(os.path.dirname(bpy.data.filepath), "prove"); os.makedirs(base, exist_ok=True)
fil = None
for spec in a[1:]:
    p = spec.split(":"); sc.camera = bpy.data.objects[p[0]]; sc.frame_set(int(p[1]))
    if len(p) > 2 and p[2] == "fil":   # fil di ferro: la geometria fatta dal codice
        if not fil:
            fil = bpy.data.materials.new("fil"); fil.use_nodes = True; nt = fil.node_tree
            wf = nt.nodes.new("ShaderNodeWireframe"); wf.use_pixel_size = True; wf.inputs["Size"].default_value = 1.4
            em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.16, 0.28, 0.9, 1); em.inputs["Strength"].default_value = 3
            tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeMixShader")
            nt.links.new(wf.outputs["Fac"], mx.inputs["Fac"]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
            nt.links.new(mx.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
            for o in sc.objects:   # al posto del donut, la sua geometria essenziale (le linee restano leggibili)
                if o.type == "MESH" and o.name not in ("fondo", "piatto"): o.hide_render = True
            bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.42, major_segments=40, minor_segments=20)
            t = bpy.context.object; t.data.materials.append(fil); t.parent = bpy.data.objects["donut"]
            for v in t.data.vertices:
                if v.co.z < 0: v.co.z *= 0.72
    sc.render.filepath = os.path.join(base, f"{p[0]}_{int(p[1]):04d}{'_fil' if len(p) > 2 else ''}.png")
    t = time.time(); bpy.ops.render.render(write_still=True); print("prova", spec, round(time.time() - t, 1), flush=True)
