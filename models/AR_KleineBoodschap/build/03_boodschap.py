"""03_boodschap Kleine Boodschap (1952, Anton Pieck): kaboutertje op een bakstenen sokkel aan de achterrand van een niervormige waterbak met bakstenen
rand (Kbvijver, Intro, Boodschap), hoge groene U-haag erachter, laag houten hekje voor de bloemenrand, grindplein naar het pad.
Kabouter (v1, statisch): jong, geen baard, blonde lokken, Pieck-blauwe puntmuts die naar achter krult met rode veer, grauwgeel shirt, blauwe broek,
rode instappers, rood capeje, rood-wit geblokte zakdoekpunten; rechtervoet op de muur (knie omhoog), linkerbeen hangt, linkerhand op de rand,
rechterhand duim omhoog (wijst naar het toiletgebouw achter hem).
Frame: oorsprong = OSM-node Kleine Boodschap = studs (-46.68, -92.28); model +X = noord, -Y = oost (kijkrichting, naar pad 1001200259).
Gebruik: Blender -b -P 03_boodschap.py -- --master KB_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"baksteen": ((0.5, 0.36, 0.3, 1), 0.85), "water": ((0.45, 0.55, 0.55, 1), 0.1), "haag": ((0.1, 0.25, 0.08, 1), 0.9), "hout": ((0.3, 0.22, 0.15, 1), 0.85),
        "huid": ((0.93, 0.76, 0.62, 1), 0.5), "blauw": ((0.2, 0.33, 0.5, 1), 0.5), "shirt": ((0.74, 0.68, 0.46, 1), 0.6), "rood": ((0.72, 0.12, 0.08, 1), 0.5),
        "ruit": ((0.85, 0.75, 0.72, 1), 0.6), "haar": ((0.9, 0.75, 0.4, 1), 0.6), "zwart": ((0.03, 0.03, 0.03, 1), 0.3), "grind": ((0.86, 0.83, 0.76, 1), 0.95),
        "modder": ((0.16, 0.12, 0.08, 1), 1.0)}
BAK = [(-1.85 * math.cos(a) * (1.0 if math.sin(a) < 0 else 0.92), 0.0 + (1.55 if math.sin(a) < 0 else 0.75) * math.sin(a) - 0.35) for a in [k * math.tau / 32 for k in range(32)]]
PLEIN = [(-5.2, -7.9), (4.8, -7.9), (4.6, -3.0), (3.0, -2.3), (2.7, -2.4), (0.0, -2.72), (-2.7, -2.4), (-3.0, -2.3), (-5.4, -3.6)]
SEAT = 0.78; GS = 1.2                                # bovenkant sokkel; schaal kabouter (beeld ~ kindergrootte)


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    def plaat(poly, z, dz, part, mat):
        tris = tessellate_polygon([[Vector((x, y, 0)) for x, y in poly]])
        bm = bmesh.new(); Tt = [bm.verts.new((x, y, z)) for x, y in poly]; Bb = [bm.verts.new((x, y, z - dz)) for x, y in poly]
        for t in tris:
            f = bm.faces.new([Tt[i] for i in t]); f.normal_update()
            if f.normal.z < 0: f.normal_flip()
            g = bm.faces.new([Bb[i] for i in t]); g.normal_update()
            if g.normal.z > 0: g.normal_flip()
        for i in range(len(poly)):
            j = (i + 1) % len(poly); bm.faces.new((Tt[i], Bb[i], Bb[j], Tt[j]))
        put(part, mat, bm)
    # ---------- waterbak: bakstenen rand (stenen in lagen), water, sokkel ----------
    n = len(BAK)
    for i in range(n):
        A, B = Vector(BAK[i]), Vector(BAK[(i + 1) % n]); L_ = (B - A).length; ang = math.atan2(B.y - A.y, B.x - A.x)
        M_ = Matrix.Translation((A.x, A.y, 0)) @ Matrix.Rotation(ang, 4, "Z")
        put("bak", "baksteen", bz(-0.02, L_ + 0.02, -0.14, 0.14, -0.15, 0.3), M_); put("bak", "baksteen", bz(-0.04, L_ + 0.04, -0.17, 0.17, 0.3, 0.36), M_)
    plaat(BAK, 0.12, 0.05, "bak", "water"); plaat(BAK, -0.2, 0.05, "bak", "modder")
    sok = bz(-0.8, 0.8, 0.2, 0.86, -0.15, SEAT, 0.02); put("bak", "baksteen", sok)
    for k in range(int(SEAT / 0.075)):                                                            # voegen-reliëf: lagen stenen
        z = k * 0.075 + 0.03; off = 0.12 if k % 2 else 0.0
        for j in range(-4, 5):
            x = j * 0.24 + off
            if abs(x) < 0.72: put("bak", "baksteen", bz(x - 0.1, x + 0.1, 0.19, 0.205, z - 0.028, z + 0.028))
    coll_box(0, -0.35, 0.18, 3.8, 2.4, 0.36); coll_box(0, 0.53, 0.4, 1.6, 0.7, 0.8)
    # ---------- de kabouter ----------
    kb = {}
    def add(mat, b_):
        kb.setdefault(mat, bmesh.new()); me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); kb[mat].from_mesh(me_); bpy.data.meshes.remove(me_)
    def V(x, y, z): return Vector((x, y, z))
    # lokaal: zitvlak z 0, heup y 0; kijkt naar -y; zijn rechterkant = -x (Intro_kleineboodschap)
    add("blauw", ell(V(0, 0.0, 0.11), (0.16, 0.14, 0.11), 12, 8))                                 # bekken/broek
    add("shirt", btube([V(0.0, 0.02, 0.15), V(0.05, 0.05, 0.38), V(0.1, 0.06, 0.55)], 0.15, 12))  # romp, leunt naar achter en naar rechts (+x)
    add("shirt", ell(V(0.05, 0.05, 0.36), (0.14, 0.11, 0.16), 12, 8))
    add("rood", ell(V(0.1, 0.02, 0.53), (0.26, 0.18, 0.13), 14, 10))   # capeje
    add("ruit", boutline([(0.0, 0.52), (0.11, 0.52), (0.06, 0.2)], -0.08, 0.02)); add("rood", boutline([(0.07, 0.52), (0.16, 0.5), (0.1, 0.26)], -0.085, 0.02))   # zakdoekpunten
    add("huid", ell(V(0.12, 0.02, 0.66), (0.045, 0.045, 0.06), 6, 4))                             # hals
    H = V(0.16, -0.01, 0.8)
    add("huid", ell(H, (0.13, 0.125, 0.15), 14, 10)); add("huid", ell(H + V(0, -0.13, -0.01), (0.04, 0.045, 0.035), 8, 6))   # groot hoofd + neus
    add("huid", ell(H + V(0, -0.08, -0.08), (0.08, 0.06, 0.05), 8, 6))                                                       # kin
    for s_ in (-1, 1):
        add("huid", ell(H + V(s_ * 0.13, 0.0, 0.0), (0.025, 0.04, 0.06), 6, 4))                   # oren
        add("zwart", ell(H + V(s_ * 0.05, -0.115, 0.035), (0.017, 0.01, 0.015), 6, 4))            # ondeugende oogjes
        add("haar", ell(H + V(s_ * 0.1, 0.03, 0.05), (0.055, 0.065, 0.06), 8, 6))                 # blonde lokken
    add("rood", btube([H + V(-0.07, -0.105, -0.055), H + V(0, -0.125, -0.075), H + V(0.07, -0.105, -0.055)], 0.013, 5))   # brede glimlach
    muts = [H + V(0, 0.02, 0.08), H + V(0.02, 0.06, 0.22), H + V(0.08, 0.13, 0.34), H + V(0.19, 0.18, 0.42), H + V(0.32, 0.16, 0.45), H + V(0.4, 0.1, 0.42)]
    rs = [0.14, 0.11, 0.08, 0.055, 0.03, 0.012]
    for i in range(5):
        add("blauw", btube([muts[i], muts[i + 1]], (rs[i] + rs[i + 1]) / 2, 10)); add("blauw", ell(muts[i + 1], (rs[i + 1],) * 3, 8, 6))
    add("blauw", ell(muts[0], (0.145, 0.145, 0.045), 12, 6))
    veer = [H + V(0.12, 0.06, 0.12), H + V(0.3, 0.08, 0.1), H + V(0.44, 0.08, 0.17), H + V(0.48, 0.06, 0.28), H + V(0.42, 0.04, 0.33), H + V(0.37, 0.04, 0.27)]
    add("rood", btube(veer, 0.022, 6))                                                              # rode krulveer
    # benen: rechts (-x) langs de muur met de knie omhoog, voet op de muur; links hangt voor de muur
    for P_ in ([V(-0.08, 0.0, 0.08), V(-0.3, -0.14, 0.33), V(-0.55, -0.06, 0.07)], [V(0.08, -0.02, 0.06), V(0.13, -0.28, 0.02), V(0.11, -0.33, -0.42)]):
        add("blauw", btube(P_, 0.078, 8)); add("blauw", ell(P_[1], (0.08,) * 3, 8, 6))
    add("rood", ell(V(-0.64, -0.07, 0.05), (0.13, 0.065, 0.045), 8, 6)); add("rood", btube([V(-0.76, -0.07, 0.05), V(-0.82, -0.07, 0.1)], 0.02, 5))
    add("rood", ell(V(0.11, -0.4, -0.46), (0.06, 0.12, 0.045), 8, 6)); add("rood", btube([V(0.11, -0.5, -0.45), V(0.11, -0.56, -0.39)], 0.02, 5))   # krul-instappers
    # armen: rechts omhoog met duim, links gestrekt opzij naar de rand
    for P_ in ([V(-0.08, 0.04, 0.52), V(-0.3, -0.02, 0.44), V(-0.36, -0.06, 0.68)], [V(0.24, 0.05, 0.5), V(0.42, 0.0, 0.3), V(0.55, -0.05, 0.04)]):
        add("shirt", btube(P_, 0.06, 8)); add("shirt", ell(P_[1], (0.06,) * 3, 8, 6))
        add("huid", ell(P_[2], (0.05, 0.055, 0.045), 8, 6))
    add("huid", btube([V(-0.36, -0.09, 0.71), V(-0.36, -0.1, 0.8)], 0.018, 6))                     # duim omhoog
    for k in range(4): add("huid", btube([V(0.55, -0.05, 0.04), V(0.58 + 0.02 * k, -0.1 - 0.03 * k, -0.02)], 0.012, 4))   # vingers over de rand
    M_K = Matrix.Translation((0.1, 0.53, SEAT)) @ Matrix.Scale(GS, 4)
    for mat, bm in kb.items():
        if mat in ("huid", "shirt", "blauw"):
            bm = organisch(bm, 0.008, 3, 0.5, 0.0, 1.0, 0.5)
        put("kabouter", mat, bm, M_K)
    # ---------- hoge groene U-haag achter en naast de bak ----------
    hg = bmesh.new()
    for i in range(15):
        a = math.pi * (0.0 + i / 14); r = 3.3
        x, y = r * math.cos(a) * 1.15, 0.9 + r * math.sin(a) * 0.55
        b_ = bz(x - 0.55, x + 0.55, y - 0.45, y + 0.45, -0.1, 1.95)
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); hg.from_mesh(me_); bpy.data.meshes.remove(me_)
    for s_ in (-1, 1):
        for k in range(3):
            y = 0.6 - k * 0.9; x = s_ * 3.8
            b_ = bz(x - 0.45, x + 0.45, y - 0.5, y + 0.5, -0.1, 1.95 - k * 0.25)
            me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); hg.from_mesh(me_); bpy.data.meshes.remove(me_)
    put("haag", "haag", organisch(hg, 0.07, 3, 0.5, 0.16, 0.7, 0.25))
    coll_box(0, 2.3, 1.0, 7.6, 1.2, 2.0); coll_box(-3.8, -0.3, 1.0, 0.9, 2.8, 2.0); coll_box(3.8, -0.3, 1.0, 0.9, 2.8, 2.0)
    # ---------- laag houten hekje voor de bloemenrand + grindplein ----------
    hek = [(-2.9, -1.0), (-2.6, -2.45), (0.0, -2.75), (2.6, -2.45), (2.9, -1.0)]
    for a, b in zip(hek, hek[1:]):
        A, B = Vector(a), Vector(b); L_ = (B - A).length; ang = math.atan2(B.y - A.y, B.x - A.x)
        M_ = Matrix.Translation((A.x, A.y, 0)) @ Matrix.Rotation(ang, 4, "Z")
        put("hek", "hout", bz(0, L_, -0.03, 0.03, 0.42, 0.5), M_); put("hek", "hout", bz(0, L_, -0.03, 0.03, 0.2, 0.26), M_)
        put("hek", "hout", bz(-0.04, 0.04, -0.04, 0.04, -0.1, 0.55), M_)
        m = (A + B) / 2; coll_box(m.x, m.y, 0.3, L_, 0.12, 0.6, math.degrees(ang))
    put("hek", "hout", bz(2.86, 2.94, -1.04, -0.96, -0.1, 0.55))
    rand = [(-2.75, -0.9), (-2.45, -2.3), (0.0, -2.6), (2.45, -2.3), (2.75, -0.9), (2.4, 0.2), (2.0, -0.2), (1.9, -1.4), (0.0, -1.95), (-1.9, -1.4), (-2.0, -0.2), (-2.4, 0.2)]
    plaat(rand, 0.1, 0.12, "bed", "modder")
    plaat(PLEIN, 0.06, 0.12, "plein", "grind")
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        o = new_mesh_object(f"KB_{part}__{mat}", bm, "FORMS"); assign(o, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "plein": PLEIN, "bak": BAK}, open(os.path.join(out, "boodschap_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
