"""04_decor: kap-interieur en hekwerk van de Sirocco (Sirocco-binnen.jpg, Overzicht_sirocco.jpg, Sirocco-reikmans.jpg,
Sirocco-kap-handelaar.jpg, Wvs-handelaar.jpg). Draai NA 03_forms (gebruikt dezelfde dakvorm).
  - hangende rieten schalen met fruit (sinaasappel, citroen, groene vruchten), puntige manden (eikelvorm), netten
  - Marokkaanse lantaarns (warm licht: ob["lamp"] = 1 -> PointLight in Roblox) en papieren lampions (oranje, rood, petrol)
  - touwen van elk ding naar het dak, touwladder in het midden (de handelaar zelf komt later als figuur)
  - gaashek met bamboepalen en touw op de rand van het vlonderdek, met twee openingen (in- en uitstappen)
Gebruik: blender --background --python build/04_decor.py -- --master AR_Sirocco_master.blend"""
import bpy, bmesh, sys, os, math, random, importlib.util
from mathutils import Vector, Matrix

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER = "phase:04_decor"
random.seed(1001)
spec = importlib.util.spec_from_file_location("forms", os.path.join(D, "build", "03_forms.py"))
src = open(os.path.join(D, "build", "03_forms.py")).read().replace("\nmain()\n", "\n")     # alleen de functies
F = {"__file__": os.path.join(D, "build", "03_forms.py"), "__name__": "forms"}
exec(compile(src, "03_forms", "exec"), F)
dak_z, DIK_RIET, VOOR = F["dak_z"], F["DIK_RIET"], F["VOOR"]
stam, cil, bol, doos = F["stam"], F["cil"], F["bol"], F["doos"]
Z_PLAT, R_SCHIJF, R_DEK = F["Z_PLAT"], F["R_SCHIJF"], F["R_DEK"]


def collectie(naam):
    c = bpy.data.collections.get(naam)
    if not c:
        c = bpy.data.collections.new(naam); bpy.context.scene.collection.children.link(c)
    return c


def obj(naam, bm, rol, **extra):
    me = bpy.data.meshes.new(naam); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(naam, me); o["owner"] = OWNER; o["rol"] = rol
    for k, v in extra.items(): o[k] = v
    collectie("LOW").objects.link(o)
    return o


def schaal(bm, c, r, diep):
    """open rieten schaal (halve bol met rand), opening boven"""
    NA, NV = 16, 5
    ringen = []
    for k in range(NV + 1):
        h = (k / NV) * math.pi / 2
        rr = r * math.sin(h) + 0.01; z = -diep * math.cos(h)
        ringen.append([bm.verts.new(Vector(c) + Vector((rr * math.cos(2 * math.pi * i / NA), rr * math.sin(2 * math.pi * i / NA), z))) for i in range(NA)])
    for k in range(NV):
        for i in range(NA):
            j = (i + 1) % NA
            bm.faces.new((ringen[k][i], ringen[k][j], ringen[k + 1][j], ringen[k + 1][i]))
    # dikke rand
    stam_ring(bm, Vector(c), r + 0.02, 0.035)


def stam_ring(bm, c, r, dik, n=16):
    pts = [c + Vector((r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), 0)) for i in range(n)]
    for i in range(n):
        stam(bm, pts[i], pts[(i + 1) % n], dik, dik, 5, 0.0)


def ophang_z(x, y): return dak_z(math.hypot(x, y), math.atan2(y, x), DIK_RIET) - 0.15


def main():
    a = sys.argv[sys.argv.index("--") + 1:]
    master = os.path.abspath(a[a.index("--master") + 1])
    bpy.ops.wm.open_mainfile(filepath=master)
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]:
        bpy.data.objects.remove(o, do_unlink=True)
    bms = {r: bmesh.new() for r in ("mand", "fruit_oranje", "fruit_geel", "fruit_groen", "touw", "lampion_oranje", "lampion_rood",
                                     "lampion_petrol", "lantaarn", "lantaarnglas", "bamboe", "net")}
    lampen = []
    # posities: ringen tussen r 1.8 en 6.6, hoogte tussen 4.2 en 1.3 m onder het dak
    items = []
    for ring_r, n in ((2.0, 6), (3.6, 9), (5.0, 12), (6.3, 13)):
        for i in range(n):
            t = 2 * math.pi * (i + random.random() * 0.6) / n
            r = ring_r + random.uniform(-0.35, 0.35)
            x, y = r * math.cos(t), r * math.sin(t)
            top = ophang_z(x, y)
            onder = max(3.4, min(top - 0.9, 3.8 + random.uniform(0, 2.4)))
            items.append((x, y, top, onder))
    soorten = ["schaal", "schaal", "schaal", "eikel", "lantaarn", "lampion", "lampion"]
    for k, (x, y, top, z) in enumerate(items):
        soort = soorten[k % len(soorten)] if k % 5 else "schaal"
        c = Vector((x, y, z))
        if soort == "schaal":
            r = random.uniform(0.35, 0.6)
            schaal(bms["mand"], c, r, r * 0.45)
            fr = random.choice(("fruit_oranje", "fruit_geel", "fruit_groen"))
            for j in range(int(r * 18)):                       # fruit opgestapeld in de schaal
                h = random.uniform(0, 2 * math.pi); rr = random.uniform(0, r * 0.75)
                bol(bms[fr], c + Vector((rr * math.cos(h), rr * math.sin(h), -0.05 + random.uniform(0, 0.12) + (1 - rr / r) * 0.08)), 0.075, 6)
            for h in (0, 2.1, 4.2):                            # drie touwen naar een haak boven de schaal
                stam(bms["touw"], c + Vector((r * math.cos(h), r * math.sin(h), 0.02)), c + Vector((0, 0, 0.9)), 0.012, 0.012, 4, 0.0)
            stam(bms["touw"], c + Vector((0, 0, 0.9)), Vector((x, y, top)), 0.018, 0.018, 4, 0.0)
        elif soort == "eikel":
            v = bol(bms["mand"], c, 0.32, 12)
            for vv in v:
                d = vv.co.z - c.z
                if d < 0: vv.co.z = c.z + d * 1.7; s = 1 + d * 0.9; vv.co.x = c.x + (vv.co.x - c.x) * s; vv.co.y = c.y + (vv.co.y - c.y) * s
            cil(bms["mand"], c + Vector((0, 0, 0.12)), 0.36, 0.1, 12)          # deksel
            stam(bms["touw"], c + Vector((0, 0, 0.22)), Vector((x, y, top)), 0.018, 0.018, 4, 0.0)
        elif soort == "lantaarn":
            cil(bms["lantaarnglas"], c + Vector((0, 0, -0.22)), 0.12, 0.34, 6, 0.15)
            cil(bms["lantaarn"], c + Vector((0, 0, 0.12)), 0.16, 0.08, 6, 0.05)
            cil(bms["lantaarn"], c + Vector((0, 0, -0.27)), 0.13, 0.05, 6)
            stam(bms["touw"], c + Vector((0, 0, 0.2)), Vector((x, y, top)), 0.015, 0.015, 4, 0.0)
            lampen.append([x, y, z - 0.05])
        else:
            kl = random.choice(("lampion_oranje", "lampion_rood", "lampion_petrol"))
            v = bol(bms[kl], c, 0.24, 12)
            for vv in v: vv.co.z = c.z + (vv.co.z - c.z) * 1.15
            cil(bms["lantaarn"], c + Vector((0, 0, 0.26)), 0.07, 0.06, 8)
            stam(bms["touw"], c + Vector((0, 0, 0.3)), Vector((x, y, top)), 0.015, 0.015, 4, 0.0)
    # touwladder in het midden (handelaar komt later), van de nok tot ~3.8 m
    zt = dak_z(0.3, 0, DIK_RIET) - 0.2
    for s in (-0.22, 0.22):
        stam(bms["touw"], (s, 0.1, zt), (s * 1.1, 0.25, 3.8), 0.022, 0.022, 4, 0.0)
    for k in range(int((zt - 3.8) / 0.35)):
        z = 3.9 + k * 0.35
        stam(bms["touw"], (-0.23, 0.1 + 0.15 * (1 - (z - 3.8) / (zt - 3.8)), z), (0.23, 0.1 + 0.15 * (1 - (z - 3.8) / (zt - 3.8)), z), 0.02, 0.02, 4, 0.0)
    # slingers van touw tussen de spanten (foto: lussen touw)
    for i in range(10):
        t = 2 * math.pi * i / 10 + 0.3
        a_, b_ = 2.5, 6.0
        p0 = Vector((a_ * math.cos(t), a_ * math.sin(t), ophang_z(a_ * math.cos(t), a_ * math.sin(t))))
        p1 = Vector((b_ * math.cos(t + 0.35), b_ * math.sin(t + 0.35), ophang_z(b_ * math.cos(t + 0.35), b_ * math.sin(t + 0.35))))
        vorig = p0
        for k in range(1, 9):
            u = k / 8; q = p0.lerp(p1, u); q.z -= math.sin(u * math.pi) * 1.1
            stam(bms["touw"], vorig, q, 0.02, 0.02, 4, 0.0); vorig = q
    # gaashek op de rand van het dek (r 7.25), 1.0 m hoog, bamboepalen om de ~1.6 m, openingen bij in- en uitstappen
    R_HEK = R_SCHIJF + 0.25
    open_hoeken = [math.radians(-62), math.radians(-106)]  # instap (einde wachtrij, luchtfoto), uitstap (uitgangsbrug op x -2)
    N = 96
    def open_(t): return any(abs((t - o + math.pi) % (2 * math.pi) - math.pi) < math.radians(9) for o in open_hoeken)
    for i in range(N):
        t0 = 2 * math.pi * i / N; t1 = 2 * math.pi * (i + 1) / N
        if open_(t0) or open_(t1): continue
        p0 = Vector((R_HEK * math.cos(t0), R_HEK * math.sin(t0), Z_PLAT)); p1 = Vector((R_HEK * math.cos(t1), R_HEK * math.sin(t1), Z_PLAT))
        vs = [bms["net"].verts.new(v) for v in (p0 + Vector((0, 0, 0.05)), p1 + Vector((0, 0, 0.05)), p1 + Vector((0, 0, 0.95)), p0 + Vector((0, 0, 0.95)))]
        bms["net"].faces.new(vs)
        vs2 = [bms["net"].verts.new(v.co) for v in vs[::-1]]; bms["net"].faces.new(vs2)       # dubbelzijdig
        stam(bms["touw"], p0 + Vector((0, 0, 0.97)), p1 + Vector((0, 0, 0.97)), 0.02, 0.02, 4, 0.0)
        if i % 3 == 0:
            stam(bms["bamboe"], p0, p0 + Vector((0, 0, 1.15)), 0.045, 0.04, 8, 0.0)
    for rol, bm in bms.items():
        if not bm.verts: bm.free(); continue
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces) if rol not in ("net", "mand") else None
        extra = {"lampen": lampen} if rol == "lantaarnglas" else {}
        obj(f"SI_decor_{rol}", bm, rol, **extra)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=master)
    print("[04_decor] klaar:", len(items), "hangende dingen,", len(lampen), "lantaarns")


main()
