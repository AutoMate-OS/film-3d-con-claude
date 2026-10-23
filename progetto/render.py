# Render di un intervallo di fotogrammi: blender -b scene.blend -P render.py -- <da> <a> [prova]
# "prova" = salva in renders/prova/ e stampa i secondi per fotogramma
import bpy, sys, os, time
a = sys.argv[sys.argv.index("--") + 1:]
da, fino = int(a[0]), int(a[1])
sc = bpy.context.scene
cart = "prova" if len(a) > 2 else "full"
base = os.path.join(os.path.dirname(bpy.data.filepath), "renders", cart)
os.makedirs(base, exist_ok=True)
passo = int(a[3]) if len(a) > 3 else 1
for f in range(da, fino + 1, passo):
    sc.frame_set(f)
    sc.render.filepath = os.path.join(base, f"f_{f:04d}.png")
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"frame {f}: {time.time() - t:.2f} s", flush=True)
